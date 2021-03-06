"""Module for querying SymPy objects about assumptions."""

from sympy.assumptions.assume import (global_assumptions, Predicate,
        AppliedPredicate)
from sympy.core import sympify
from sympy.core.cache import cacheit
from sympy.core.relational import Relational
from sympy.core.kind import BooleanKind
from sympy.logic.boolalg import (to_cnf, And, Not, Or, Implies, Equivalent)
from sympy.logic.inference import satisfiable
from sympy.utilities.decorator import memoize_property
from sympy.assumptions.cnf import CNF, EncodedCNF, Literal


# Memoization is necessary for the properties of AssumptionKeys to
# ensure that only one object of Predicate objects are created.
# This is because assumption handlers are registered on those objects.


class AssumptionKeys:
    """
    This class contains all the supported keys by ``ask``.
    It should be accessed via the instance ``sympy.Q``.

    """

    # DO NOT add methods or properties other than predicate keys.
    # SAT solver checks the properties of Q and use them to compute the
    # fact system. Non-predicate attributes will break this.

    @memoize_property
    def hermitian(self):
        from .handlers.sets import HermitianPredicate
        return HermitianPredicate()

    @memoize_property
    def antihermitian(self):
        from .handlers.sets import AntihermitianPredicate
        return AntihermitianPredicate()

    @memoize_property
    def real(self):
        from .handlers.sets import RealPredicate
        return RealPredicate()

    @memoize_property
    def extended_real(self):
        from .handlers.sets import ExtendedRealPredicate
        return ExtendedRealPredicate()

    @memoize_property
    def imaginary(self):
        from .handlers.sets import ImaginaryPredicate
        return ImaginaryPredicate()

    @memoize_property
    def complex(self):
        from .handlers.sets import ComplexPredicate
        return ComplexPredicate()

    @memoize_property
    def algebraic(self):
        from .handlers.sets import AlgebraicPredicate
        return AlgebraicPredicate()

    @memoize_property
    def transcendental(self):
        from .predicates.sets import TranscendentalPredicate
        return TranscendentalPredicate()

    @memoize_property
    def integer(self):
        from .handlers.sets import IntegerPredicate
        return IntegerPredicate()

    @memoize_property
    def rational(self):
        from .handlers.sets import RationalPredicate
        return RationalPredicate()

    @memoize_property
    def irrational(self):
        from .handlers.sets import IrrationalPredicate
        return IrrationalPredicate()

    @memoize_property
    def finite(self):
        from .handlers.calculus import FinitePredicate
        return FinitePredicate()

    @memoize_property
    def infinite(self):
        from .predicates.calculus import InfinitePredicate
        return InfinitePredicate()

    @memoize_property
    def positive(self):
        from .handlers.order import PositivePredicate
        return PositivePredicate()

    @memoize_property
    def negative(self):
        from .handlers.order import NegativePredicate
        return NegativePredicate()

    @memoize_property
    def zero(self):
        from .handlers.order import ZeroPredicate
        return ZeroPredicate()

    @memoize_property
    def nonzero(self):
        from .handlers.order import NonZeroPredicate
        return NonZeroPredicate()

    @memoize_property
    def nonpositive(self):
        from .handlers.order import NonPositivePredicate
        return NonPositivePredicate()

    @memoize_property
    def nonnegative(self):
        from .handlers.order import NonNegativePredicate
        return NonNegativePredicate()

    @memoize_property
    def even(self):
        from .handlers.ntheory import EvenPredicate
        return EvenPredicate()

    @memoize_property
    def odd(self):
        from .handlers.ntheory import OddPredicate
        return OddPredicate()

    @memoize_property
    def prime(self):
        from .handlers.ntheory import PrimePredicate
        return PrimePredicate()

    @memoize_property
    def composite(self):
        from .handlers.ntheory import CompositePredicate
        return CompositePredicate()

    @memoize_property
    def commutative(self):
        """
        Commutative predicate.

        Explanation
        ===========

        ``ask(Q.commutative(x))`` is true iff ``x`` commutes with any other
        object with respect to multiplication operation.

        """
        # TODO: Add examples
        return Predicate('commutative')

    @memoize_property
    def is_true(self):
        """
        Generic predicate.

        Explanation
        ===========

        ``ask(Q.is_true(x))`` is true iff ``x`` is true. This only makes
        sense if ``x`` is a predicate.

        Examples
        ========

        >>> from sympy import ask, Q, symbols
        >>> x = symbols('x')
        >>> ask(Q.is_true(True))
        True

        """
        return Predicate('is_true')

    @memoize_property
    def symmetric(self):
        """
        Symmetric matrix predicate.

        Explanation
        ===========

        ``Q.symmetric(x)`` is true iff ``x`` is a square matrix and is equal to
        its transpose. Every square diagonal matrix is a symmetric matrix.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 2, 2)
        >>> Y = MatrixSymbol('Y', 2, 3)
        >>> Z = MatrixSymbol('Z', 2, 2)
        >>> ask(Q.symmetric(X*Z), Q.symmetric(X) & Q.symmetric(Z))
        True
        >>> ask(Q.symmetric(X + Z), Q.symmetric(X) & Q.symmetric(Z))
        True
        >>> ask(Q.symmetric(Y))
        False


        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Symmetric_matrix

        """
        # TODO: Add handlers to make these keys work with
        # actual matrices and add more examples in the docstring.
        return Predicate('symmetric')

    @memoize_property
    def invertible(self):
        """
        Invertible matrix predicate.

        Explanation
        ===========

        ``Q.invertible(x)`` is true iff ``x`` is an invertible matrix.
        A square matrix is called invertible only if its determinant is 0.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 2, 2)
        >>> Y = MatrixSymbol('Y', 2, 3)
        >>> Z = MatrixSymbol('Z', 2, 2)
        >>> ask(Q.invertible(X*Y), Q.invertible(X))
        False
        >>> ask(Q.invertible(X*Z), Q.invertible(X) & Q.invertible(Z))
        True
        >>> ask(Q.invertible(X), Q.fullrank(X) & Q.square(X))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Invertible_matrix

        """
        return Predicate('invertible')

    @memoize_property
    def orthogonal(self):
        """
        Orthogonal matrix predicate.

        Explanation
        ===========

        ``Q.orthogonal(x)`` is true iff ``x`` is an orthogonal matrix.
        A square matrix ``M`` is an orthogonal matrix if it satisfies
        ``M^TM = MM^T = I`` where ``M^T`` is the transpose matrix of
        ``M`` and ``I`` is an identity matrix. Note that an orthogonal
        matrix is necessarily invertible.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol, Identity
        >>> X = MatrixSymbol('X', 2, 2)
        >>> Y = MatrixSymbol('Y', 2, 3)
        >>> Z = MatrixSymbol('Z', 2, 2)
        >>> ask(Q.orthogonal(Y))
        False
        >>> ask(Q.orthogonal(X*Z*X), Q.orthogonal(X) & Q.orthogonal(Z))
        True
        >>> ask(Q.orthogonal(Identity(3)))
        True
        >>> ask(Q.invertible(X), Q.orthogonal(X))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Orthogonal_matrix

        """
        return Predicate('orthogonal')

    @memoize_property
    def unitary(self):
        """
        Unitary matrix predicate.

        Explanation
        ===========

        ``Q.unitary(x)`` is true iff ``x`` is a unitary matrix.
        Unitary matrix is an analogue to orthogonal matrix. A square
        matrix ``M`` with complex elements is unitary if :math:``M^TM = MM^T= I``
        where :math:``M^T`` is the conjugate transpose matrix of ``M``.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol, Identity
        >>> X = MatrixSymbol('X', 2, 2)
        >>> Y = MatrixSymbol('Y', 2, 3)
        >>> Z = MatrixSymbol('Z', 2, 2)
        >>> ask(Q.unitary(Y))
        False
        >>> ask(Q.unitary(X*Z*X), Q.unitary(X) & Q.unitary(Z))
        True
        >>> ask(Q.unitary(Identity(3)))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Unitary_matrix

        """
        return Predicate('unitary')

    @memoize_property
    def positive_definite(self):
        r"""
        Positive definite matrix predicate.

        Explanation
        ===========

        If ``M`` is a :math:``n \times n`` symmetric real matrix, it is said
        to be positive definite if :math:`Z^TMZ` is positive for
        every non-zero column vector ``Z`` of ``n`` real numbers.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol, Identity
        >>> X = MatrixSymbol('X', 2, 2)
        >>> Y = MatrixSymbol('Y', 2, 3)
        >>> Z = MatrixSymbol('Z', 2, 2)
        >>> ask(Q.positive_definite(Y))
        False
        >>> ask(Q.positive_definite(Identity(3)))
        True
        >>> ask(Q.positive_definite(X + Z), Q.positive_definite(X) &
        ...     Q.positive_definite(Z))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Positive-definite_matrix

        """
        return Predicate('positive_definite')

    @memoize_property
    def upper_triangular(self):
        """
        Upper triangular matrix predicate.

        Explanation
        ===========

        A matrix ``M`` is called upper triangular matrix if :math:`M_{ij}=0`
        for :math:`i<j`.

        Examples
        ========

        >>> from sympy import Q, ask, ZeroMatrix, Identity
        >>> ask(Q.upper_triangular(Identity(3)))
        True
        >>> ask(Q.upper_triangular(ZeroMatrix(3, 3)))
        True

        References
        ==========

        .. [1] http://mathworld.wolfram.com/UpperTriangularMatrix.html

        """
        return Predicate('upper_triangular')

    @memoize_property
    def lower_triangular(self):
        """
        Lower triangular matrix predicate.

        Explanation
        ===========

        A matrix ``M`` is called lower triangular matrix if :math:`a_{ij}=0`
        for :math:`i>j`.

        Examples
        ========

        >>> from sympy import Q, ask, ZeroMatrix, Identity
        >>> ask(Q.lower_triangular(Identity(3)))
        True
        >>> ask(Q.lower_triangular(ZeroMatrix(3, 3)))
        True

        References
        ==========

        .. [1] http://mathworld.wolfram.com/LowerTriangularMatrix.html
        """
        return Predicate('lower_triangular')

    @memoize_property
    def diagonal(self):
        """
        Diagonal matrix predicate.

        Explanation
        ===========

        ``Q.diagonal(x)`` is true iff ``x`` is a diagonal matrix. A diagonal
        matrix is a matrix in which the entries outside the main diagonal
        are all zero.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol, ZeroMatrix
        >>> X = MatrixSymbol('X', 2, 2)
        >>> ask(Q.diagonal(ZeroMatrix(3, 3)))
        True
        >>> ask(Q.diagonal(X), Q.lower_triangular(X) &
        ...     Q.upper_triangular(X))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Diagonal_matrix

        """
        return Predicate('diagonal')

    @memoize_property
    def fullrank(self):
        """
        Fullrank matrix predicate.

        Explanation
        ===========

        ``Q.fullrank(x)`` is true iff ``x`` is a full rank matrix.
        A matrix is full rank if all rows and columns of the matrix
        are linearly independent. A square matrix is full rank iff
        its determinant is nonzero.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol, ZeroMatrix, Identity
        >>> X = MatrixSymbol('X', 2, 2)
        >>> ask(Q.fullrank(X.T), Q.fullrank(X))
        True
        >>> ask(Q.fullrank(ZeroMatrix(3, 3)))
        False
        >>> ask(Q.fullrank(Identity(3)))
        True

        """
        return Predicate('fullrank')

    @memoize_property
    def square(self):
        """
        Square matrix predicate.

        Explanation
        ===========

        ``Q.square(x)`` is true iff ``x`` is a square matrix. A square matrix
        is a matrix with the same number of rows and columns.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol, ZeroMatrix, Identity
        >>> X = MatrixSymbol('X', 2, 2)
        >>> Y = MatrixSymbol('X', 2, 3)
        >>> ask(Q.square(X))
        True
        >>> ask(Q.square(Y))
        False
        >>> ask(Q.square(ZeroMatrix(3, 3)))
        True
        >>> ask(Q.square(Identity(3)))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Square_matrix

        """
        return Predicate('square')

    @memoize_property
    def integer_elements(self):
        """
        Integer elements matrix predicate.

        Explanation
        ===========

        ``Q.integer_elements(x)`` is true iff all the elements of ``x``
        are integers.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.integer(X[1, 2]), Q.integer_elements(X))
        True

        """
        return Predicate('integer_elements')

    @memoize_property
    def real_elements(self):
        """
        Real elements matrix predicate.

        Explanation
        ===========

        ``Q.real_elements(x)`` is true iff all the elements of ``x``
        are real numbers.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.real(X[1, 2]), Q.real_elements(X))
        True

        """
        return Predicate('real_elements')

    @memoize_property
    def complex_elements(self):
        """
        Complex elements matrix predicate.

        Explanation
        ===========

        ``Q.complex_elements(x)`` is true iff all the elements of ``x``
        are complex numbers.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.complex(X[1, 2]), Q.complex_elements(X))
        True
        >>> ask(Q.complex_elements(X), Q.integer_elements(X))
        True

        """
        return Predicate('complex_elements')

    @memoize_property
    def singular(self):
        """
        Singular matrix predicate.

        A matrix is singular iff the value of its determinant is 0.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.singular(X), Q.invertible(X))
        False
        >>> ask(Q.singular(X), ~Q.invertible(X))
        True

        References
        ==========

        .. [1] http://mathworld.wolfram.com/SingularMatrix.html

        """
        return Predicate('singular')

    @memoize_property
    def normal(self):
        """
        Normal matrix predicate.

        A matrix is normal if it commutes with its conjugate transpose.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.normal(X), Q.unitary(X))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Normal_matrix

        """
        return Predicate('normal')

    @memoize_property
    def triangular(self):
        """
        Triangular matrix predicate.

        Explanation
        ===========

        ``Q.triangular(X)`` is true if ``X`` is one that is either lower
        triangular or upper triangular.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.triangular(X), Q.upper_triangular(X))
        True
        >>> ask(Q.triangular(X), Q.lower_triangular(X))
        True

        References
        ==========

        .. [1] https://en.wikipedia.org/wiki/Triangular_matrix

        """
        return Predicate('triangular')

    @memoize_property
    def unit_triangular(self):
        """
        Unit triangular matrix predicate.

        Explanation
        ===========

        A unit triangular matrix is a triangular matrix with 1s
        on the diagonal.

        Examples
        ========

        >>> from sympy import Q, ask, MatrixSymbol
        >>> X = MatrixSymbol('X', 4, 4)
        >>> ask(Q.triangular(X), Q.unit_triangular(X))
        True

        """
        return Predicate('unit_triangular')


Q = AssumptionKeys()

def _extract_facts(expr, symbol, check_reversed_rel=True):
    """
    Helper for ask().

    Explanation
    ===========

    Extracts the facts relevant to the symbol from an assumption.
    Returns None if there is nothing to extract.
    """
    if isinstance(symbol, Relational):
        if check_reversed_rel:
            rev = _extract_facts(expr, symbol.reversed, False)
            if rev is not None:
                return rev
    if isinstance(expr, bool):
        return
    if not expr.has(symbol):
        return
    if isinstance(expr, AppliedPredicate):
        if expr.arg == symbol:
            return expr.func
        else:
            return
    if isinstance(expr, Not) and expr.args[0].func in (And, Or):
        cls = Or if expr.args[0] == And else And
        expr = cls(*[~arg for arg in expr.args[0].args])
    args = [_extract_facts(arg, symbol) for arg in expr.args]
    if isinstance(expr, And):
        args = [x for x in args if x is not None]
        if args:
            return expr.func(*args)
    if args and all(x is not None for x in args):
        return expr.func(*args)


def _extract_all_facts(expr, symbols):
    facts = set()
    if len(symbols) == 1 and isinstance(symbols[0], Relational):
        rel = symbols[0]
        symbols = (rel, rel.reversed)

    for clause in expr.clauses:
        args = []
        for literal in clause:
            if isinstance(literal.lit, AppliedPredicate):
                if literal.lit.arg in symbols:
                    # Add literal if it has 'symbol' in it
                    args.append(Literal(literal.lit.func, literal.is_Not))
                else:
                    # If any of the literals doesn't have 'symbol' don't add the whole clause.
                    break
        else:
            if args:
                facts.add(frozenset(args))
    return CNF(facts)


def ask(proposition, assumptions=True, context=global_assumptions):
    """
    Function to evaluate the proposition with assumptions.

    **Syntax**

        * ask(proposition)
            Evaluate the *proposition* in global assumption context.

        * ask(proposition, assumptions)
            Evaluate the *proposition* with respect to *assumptions* in
            global assumption context.

    This function evaluates the proposition to ``True`` or ``False`` if
    the truth value can be determined. If not, it returns ``None``.
    It should be discerned from :func:`~.refine()` which does not reduce
    the expression to ``None``.

    Parameters
    ==========

    proposition : any boolean expression
        Proposition which will be evaluated to boolean value. If this is
        not ``AppliedPredicate``, it will be wrapped by ``Q.is_true``.

    assumptions : any boolean expression, optional
        Local assumptions to evaluate the *proposition*.

    context : AssumptionsContext, optional
        Default assumptions to evaluate the *proposition*. By default,
        this is ``sympy.assumptions.global_assumptions`` variable.

    Examples
    ========

    >>> from sympy import ask, Q, pi
    >>> from sympy.abc import x, y
    >>> ask(Q.rational(pi))
    False
    >>> ask(Q.even(x*y), Q.even(x) & Q.integer(y))
    True
    >>> ask(Q.prime(4*x), Q.integer(x))
    False

    If the truth value cannot be determined, ``None`` will be returned.

    >>> print(ask(Q.odd(3*x))) # cannot determine unless we know x
    None

    **Remarks**

        Relations in assumptions are not implemented (yet), so the following
        will not give a meaningful result.

        >>> ask(Q.positive(x), Q.is_true(x > 0))

        It is however a work in progress.

    See Also
    ========

    sympy.assumptions.refine.refine : Simplification using assumptions.
        Proposition is not reduced to ``None`` if the truth value cannot
        be determined.
    """
    from sympy.assumptions.satask import satask

    proposition = sympify(proposition)
    assumptions = sympify(assumptions)

    if isinstance(proposition, Predicate) or proposition.kind is not BooleanKind:
        raise TypeError("proposition must be a valid logical expression")

    if isinstance(assumptions, Predicate) or assumptions.kind is not BooleanKind:
        raise TypeError("assumptions must be a valid logical expression")

    if isinstance(proposition, AppliedPredicate):
        key, args = proposition.function, proposition.arguments
    else:
        key, args = Q.is_true, (proposition,)

    assump = CNF.from_prop(assumptions)
    assump.extend(context)

    local_facts = _extract_all_facts(assump, args)

    known_facts_cnf = get_all_known_facts()
    known_facts_dict = get_known_facts_dict()

    enc_cnf = EncodedCNF()
    enc_cnf.from_cnf(CNF(known_facts_cnf))
    enc_cnf.add_from_cnf(local_facts)

    if local_facts.clauses and satisfiable(enc_cnf) is False:
        raise ValueError("inconsistent assumptions %s" % assumptions)

    if local_facts.clauses:

        if len(local_facts.clauses) == 1:
            cl, = local_facts.clauses
            f, = cl if len(cl)==1 else [None]
            if f and f.is_Not and f.arg in known_facts_dict.get(key, []):
                return False

        for clause in local_facts.clauses:
            if len(clause) == 1:
                f, = clause
                fdict = known_facts_dict.get(f.arg, None) if not f.is_Not else None
                if fdict and key in fdict:
                    return True
                if fdict and Not(key) in known_facts_dict[f.arg]:
                    return False

    # direct resolution method, no logic
    res = key(*args)._eval_ask(assumptions)
    if res is not None:
        return bool(res)
    # using satask (still costly)
    res = satask(proposition, assumptions=assumptions, context=context)
    return res


def ask_full_inference(proposition, assumptions, known_facts_cnf):
    """
    Method for inferring properties about objects.

    """
    if not satisfiable(And(known_facts_cnf, assumptions, proposition)):
        return False
    if not satisfiable(And(known_facts_cnf, assumptions, Not(proposition))):
        return True
    return None


def register_handler(key, handler):
    """
    Register a handler in the ask system. key must be a string and handler a
    class inheriting from AskHandler::

        >>> from sympy.assumptions import register_handler, ask, Q
        >>> from sympy.assumptions.handlers import AskHandler
        >>> class MersenneHandler(AskHandler):
        ...     # Mersenne numbers are in the form 2**n - 1, n integer
        ...     @staticmethod
        ...     def Integer(expr, assumptions):
        ...         from sympy import log
        ...         return ask(Q.integer(log(expr + 1, 2)))
        >>> register_handler('mersenne', MersenneHandler)
        >>> ask(Q.mersenne(7))
        True

    """
    # Will be deprecated
    if isinstance(key, Predicate):
        key = key.name.name
    Qkey = getattr(Q, key, None)
    if Qkey is not None:
        Qkey.add_handler(handler)
    else:
        setattr(Q, key, Predicate(key, handlers=[handler]))


def remove_handler(key, handler):
    """Removes a handler from the ask system. Same syntax as register_handler"""
    # Will be deprecated
    if isinstance(key, Predicate):
        key = key.name.name
    getattr(Q, key).remove_handler(handler)


def single_fact_lookup(known_facts_keys, known_facts_cnf):
    # Compute the quick lookup for single facts
    mapping = {}
    for key in known_facts_keys:
        mapping[key] = {key}
        for other_key in known_facts_keys:
            if other_key != key:
                if ask_full_inference(other_key, key, known_facts_cnf):
                    mapping[key].add(other_key)
    return mapping


def compute_known_facts(known_facts, known_facts_keys):
    """Compute the various forms of knowledge compilation used by the
    assumptions system.

    Explanation
    ===========

    This function is typically applied to the results of the ``get_known_facts``
    and ``get_known_facts_keys`` functions defined at the bottom of
    this file.
    """
    from textwrap import dedent, wrap

    fact_string = dedent('''\
    """
    The contents of this file are the return value of
    ``sympy.assumptions.ask.compute_known_facts``.

    Do NOT manually edit this file.
    Instead, run ./bin/ask_update.py.
    """

    from sympy.core.cache import cacheit
    from sympy.logic.boolalg import And
    from sympy.assumptions.cnf import Literal
    from sympy.assumptions.ask import Q

    # -{ Known facts as a set }-
    @cacheit
    def get_all_known_facts():
        return {
            %s
        }

    # -{ Known facts in Conjunctive Normal Form }-
    @cacheit
    def get_known_facts_cnf():
        return And(
            %s
        )

    # -{ Known facts in compressed sets }-
    @cacheit
    def get_known_facts_dict():
        return {
            %s
        }
    ''')
    # Compute the known facts in CNF form for logical inference
    LINE = ",\n        "
    HANG = ' '*8
    cnf = to_cnf(known_facts)
    cnf_ = CNF.to_CNF(known_facts)
    c = LINE.join([str(a) for a in cnf.args])

    p = LINE.join(sorted(['frozenset((' + ', '.join(str(lit) for lit in sorted(clause, key=str)) +'))' for clause in cnf_.clauses]))
    mapping = single_fact_lookup(known_facts_keys, cnf)
    items = sorted(mapping.items(), key=str)
    keys = [str(i[0]) for i in items]
    values = ['set(%s)' % sorted(i[1], key=str) for i in items]
    m = LINE.join(['\n'.join(
        wrap("{}: {}".format(k, v),
            subsequent_indent=HANG,
            break_long_words=False))
        for k, v in zip(keys, values)]) + ','
    return fact_string % (p, c, m)

# handlers tells us what ask handler we should use
# for a particular key
_val_template = 'sympy.assumptions.handlers.%s'
_handlers = [
    ("commutative",       "AskCommutativeHandler"),
    ("is_true",           "common.TautologicalHandler"),
    ("symmetric",         "matrices.AskSymmetricHandler"),
    ("invertible",        "matrices.AskInvertibleHandler"),
    ("orthogonal",        "matrices.AskOrthogonalHandler"),
    ("unitary",           "matrices.AskUnitaryHandler"),
    ("positive_definite", "matrices.AskPositiveDefiniteHandler"),
    ("upper_triangular",  "matrices.AskUpperTriangularHandler"),
    ("lower_triangular",  "matrices.AskLowerTriangularHandler"),
    ("diagonal",          "matrices.AskDiagonalHandler"),
    ("fullrank",          "matrices.AskFullRankHandler"),
    ("square",            "matrices.AskSquareHandler"),
    ("integer_elements",  "matrices.AskIntegerElementsHandler"),
    ("real_elements",     "matrices.AskRealElementsHandler"),
    ("complex_elements",  "matrices.AskComplexElementsHandler"),
]

for name, value in _handlers:
    register_handler(name, _val_template % value)

@cacheit
def get_known_facts_keys():
    return [
        getattr(Q, attr)
        for attr in Q.__class__.__dict__
        if not attr.startswith('__')]

@cacheit
def get_known_facts():
    return And(
        Implies(Q.infinite, ~Q.finite),
        Implies(Q.real, Q.complex),
        Implies(Q.real, Q.hermitian),
        Equivalent(Q.extended_real, Q.real | Q.infinite),
        Equivalent(Q.even | Q.odd, Q.integer),
        Implies(Q.even, ~Q.odd),
        Implies(Q.prime, Q.integer & Q.positive & ~Q.composite),
        Implies(Q.integer, Q.rational),
        Implies(Q.rational, Q.algebraic),
        Implies(Q.algebraic, Q.complex),
        Implies(Q.algebraic, Q.finite),
        Equivalent(Q.transcendental | Q.algebraic, Q.complex & Q.finite),
        Implies(Q.transcendental, ~Q.algebraic),
        Implies(Q.transcendental, Q.finite),
        Implies(Q.imaginary, Q.complex & ~Q.real),
        Implies(Q.imaginary, Q.antihermitian),
        Implies(Q.antihermitian, ~Q.hermitian),
        Equivalent(Q.irrational | Q.rational, Q.real & Q.finite),
        Implies(Q.irrational, ~Q.rational),
        Implies(Q.zero, Q.even),

        Equivalent(Q.real, Q.negative | Q.zero | Q.positive),
        Implies(Q.zero, ~Q.negative & ~Q.positive),
        Implies(Q.negative, ~Q.positive),
        Equivalent(Q.nonnegative, Q.zero | Q.positive),
        Equivalent(Q.nonpositive, Q.zero | Q.negative),
        Equivalent(Q.nonzero, Q.negative | Q.positive),

        Implies(Q.orthogonal, Q.positive_definite),
        Implies(Q.orthogonal, Q.unitary),
        Implies(Q.unitary & Q.real, Q.orthogonal),
        Implies(Q.unitary, Q.normal),
        Implies(Q.unitary, Q.invertible),
        Implies(Q.normal, Q.square),
        Implies(Q.diagonal, Q.normal),
        Implies(Q.positive_definite, Q.invertible),
        Implies(Q.diagonal, Q.upper_triangular),
        Implies(Q.diagonal, Q.lower_triangular),
        Implies(Q.lower_triangular, Q.triangular),
        Implies(Q.upper_triangular, Q.triangular),
        Implies(Q.triangular, Q.upper_triangular | Q.lower_triangular),
        Implies(Q.upper_triangular & Q.lower_triangular, Q.diagonal),
        Implies(Q.diagonal, Q.symmetric),
        Implies(Q.unit_triangular, Q.triangular),
        Implies(Q.invertible, Q.fullrank),
        Implies(Q.invertible, Q.square),
        Implies(Q.symmetric, Q.square),
        Implies(Q.fullrank & Q.square, Q.invertible),
        Equivalent(Q.invertible, ~Q.singular),
        Implies(Q.integer_elements, Q.real_elements),
        Implies(Q.real_elements, Q.complex_elements),
    )

from sympy.assumptions.ask_generated import (
    get_known_facts_dict, get_all_known_facts)

import sys
from pair import *
from scheme_utils import *
from ucb import main, trace

from scheme_classes import *
import scheme_forms

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, _=None): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR based on Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # Evaluate atoms
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr

    # All non-atomic expressions should be lists (combinations), which represents procedure calls
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest
    if scheme_symbolp(first):
        if first in scheme_forms.SPECIAL_FORMS:
            return scheme_forms.SPECIAL_FORMS[first](rest, env)
        else:
            procedure = env.lookup(first) # could be an SchemeError if first is not in env
            return scheme_apply(procedure, rest, env)
    else:
        procedure = scheme_eval(first, env) 
        return scheme_apply(procedure, rest, env)
        
def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    validate_procedure(procedure)
    if not isinstance(env, Frame):
       assert False, "Not a Frame: {}".format(env)
    if isinstance(procedure, BuiltinProcedure):
        func_py = procedure.py_func 
        args_evaluated = []
        while args is not nil:
            args_evaluated.append(scheme_eval(args.first, env))
            args = args.rest
        if procedure.need_env:
            args_evaluated.append(env)
        try:
            return func_py(*args_evaluated)
        except TypeError as err:
            raise SchemeError('incorrect number of arguments: {0}'.format(procedure))
    elif isinstance(procedure, LambdaProcedure):
        """
        evaluate the arguments in the current environment and take them as formals in the running environment of the lambda function, 
        . which is a child frame of the lambda's environment
        """
        # Evaluate arguments
        cur = args
        while cur is not nil:
            cur.first = scheme_eval(cur.first, env)
            cur = cur.rest
        # Run the procedure on the child frame which contains the bound oprends and takes the frame where lamba was built as parent
        env_temp = procedure.env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, env_temp)
    elif isinstance(procedure, MuProcedure):
        # Evaluate arguments
        cur = args
        while cur is not nil:
            cur.first = scheme_eval(cur.first, env)
            cur = cur.rest
        # Run the procedure on the child frame which contains the bound oprends and takes the current frame as parent
        env_temp = env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, env_temp)
    else:
        assert False, "Unexpected procedure: {}".format(procedure)

def eval_all(expressions, env):
    """Evaluate each expression in the Scheme list EXPRESSIONS in
    Frame ENV (the current environment) and return the value of the last.

    >>> eval_all(read_line("(1)"), create_global_frame())
    1
    >>> eval_all(read_line("(1 2)"), create_global_frame())
    2
    >>> x = eval_all(read_line("((print 1) 2)"), create_global_frame())
    1
    >>> x
    2
    >>> eval_all(read_line("((define x 2) x)"), create_global_frame())
    2
    """
    res = None
    while expressions is not nil:
        res = scheme_eval(expressions.first, env)
        expressions = expressions.rest
    return res



################################
# Extra Credit: Tail Recursion #
################################

class Unevaluated:
    """An expression and an environment in which it is to be evaluated."""

    def __init__(self, expr, env):
        """Expression EXPR to be evaluated in Frame ENV."""
        self.expr = expr
        self.env = env

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not an Unevaluated."""
    validate_procedure(procedure)
    val = scheme_apply(procedure, args, env)
    if isinstance(val, Unevaluated):
        return scheme_eval(val.expr, val.env)
    else:
        return val

def optimize_tail_calls(unoptimized_scheme_eval):
    """Return a properly tail recursive version of an eval function."""
    def optimized_eval(expr, env, tail=False):
        """Evaluate Scheme expression EXPR in Frame ENV. If TAIL,
        return an Unevaluated containing an expression for further evaluation.
        """
        if tail and not scheme_symbolp(expr) and not self_evaluating(expr):
            return Unevaluated(expr, env)

        result = Unevaluated(expr, env)
        # BEGIN OPTIONAL PROBLEM 1
        "*** YOUR CODE HERE ***"
        # END OPTIONAL PROBLEM 1
    return optimized_eval




def test_nested_lambda_scoping():
    """Test lexical scoping in nested lambdas
    
    >>> from scheme import *
    >>> env = create_global_frame()
    
    # Step 1: Define x in global frame
    >>> scheme_eval(read_line("(define x 5)"), env)
    'x'
    >>> env.lookup('x')
    5
    
    # Step 2: Define outer lambda
    >>> scheme_eval(read_line("(define outer (lambda (x) (lambda () (print x))))"), env)
    'outer'
    >>> isinstance(env.lookup('outer'), LambdaProcedure)
    True
    
    # Step 3: Create inner lambda with x=2
    >>> scheme_eval(read_line("(define inner (outer 2))"), env)
    'inner'
    >>> inner_proc = env.lookup('inner')
    >>> isinstance(inner_proc, LambdaProcedure)
    True
    >>> inner_proc.env.lookup('x')  # Should find x=2 in captured env
    2
    
    # Step 4: Call inner lambda
    >>> scheme_eval(read_line("(inner)"), env)
    2
    """





################################################################
# Uncomment the following line to apply tail call optimization #
################################################################

# scheme_eval = optimize_tail_calls(scheme_eval)

# fuzzgetenv

Sample getenv fuzzer designed to be able to fuzz embedded Linux targets.

# Dependencies

Runs under Linux. Requires python3 and gcc.

# Example usage

First, compile the examples by running `make examples`. Next, you can run the fuzzer against a simple example by executing `python3 fuzzenv.py outputdir ./examples/vuln`.


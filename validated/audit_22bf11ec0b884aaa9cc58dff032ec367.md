Looking at the codebase, I need to find an analog to the pattern: **a function that modifies critical state without checking a required invariant that other similar functions enforce**.

Let me examine the three `respond*` functions and their verification patterns.
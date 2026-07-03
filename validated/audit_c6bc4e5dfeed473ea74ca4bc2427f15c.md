Looking at the vulnerability class — **unbounded iteration over a user-controlled list causing fund freeze** — I need to find an analog in LRT-rsETH where an unprivileged user can cause a loop to grow unboundedly, leading to gas exhaustion and fund freeze.

The most direct analog is in `KernelDepositPool.claimWithdrawal()`.
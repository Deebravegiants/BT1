Looking at the external report's vulnerability class — a privileged role accepting a caller-supplied address parameter and using it to redirect assets without enforcing authorization — I need to find an analog in Chia's production code.

The most relevant area is the CHIP-22 third-party harvester protocol, specifically the `farmer_reward_address_override` mechanism.
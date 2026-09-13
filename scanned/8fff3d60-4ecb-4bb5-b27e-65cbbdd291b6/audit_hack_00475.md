# [C] Kelp DAO incident: LayerZero issued a statement saying that on April 18, Kelp DAO suffered an attack resulting in approximately $290 million in losse

## Summary
Severity: Critical
Target: Kelp DAO
Loss: $ 293,000,000
Attack method: Supply Chain Attack
Published: 2026-04-18
Source: https://x.com/LayerZero_Core/status/2046081551574983137
Type: slowmist-incident

## Details
LayerZero issued a statement saying that on April 18, Kelp DAO suffered an attack resulting in approximately $290 million in losses. The incident is initially assessed to have been carried out by a highly sophisticated nation-state actor, suspected to be the TraderTraitor subgroup of North Korea’s Lazarus Group. The attack was completely isolated to Kelp DAO’s rsETH configuration and was caused by its use of a single DVN (Decentralized Verifier Network) setup. The LayerZero protocol itself was not exploited, and no other cross-chain assets or applications were affected. The core of the attack involved the hacker compromising downstream RPC infrastructure used by LayerZero’s DVN. The attacker obtained the RPC node list used by the DVN, then infiltrated two independent RPC nodes. They replaced the op-geth binary and used a custom payload to forge messages. This setup allowed the attacker to display false data only to the DVN, while showing correct data to other observers, including LayerZero Scan. The attacker then launched a DDoS attack against the uncompromised RPC nodes, forcing a failover to the poisoned RPC nodes. As a result, the DVN accepted the falsified messages, enabling the attack to succeed. After the attack was completed, the attacker removed the malicious binaries, logs, and configuration files. LayerZero has since decommissioned all affected RPC nodes, replaced them, and confirmed that the DVN has returned to normal operation.

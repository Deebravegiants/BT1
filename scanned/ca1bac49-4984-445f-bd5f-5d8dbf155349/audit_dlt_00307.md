# [M] EL-2026-18: Recursive CALL with SELFDESTRUCT causes excessive execution time

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Source: https://notes.ethereum.org/qalqTnvEQkiFg6uTC20fWA
Type: ef-disclosure

## Details
using Ethereum.Test.Base.Interfaces;
using Ethereum.Test.Base;
using Nethermind.Consensus.Validators;
using Nethermind.Core.Crypto;
using Nethermind.Core.Extensions;
using Nethermind.Core.Specs;
using Nethermind.Core.Test.Builders;
using Nethermind.Core;
using Nethermind.Crypto;
using Nethermind.Db;
using Nethermind.Evm.Test;
using Nethermind.Evm.Tracing;
using Nethermind.Evm.TransactionProcessing;
using Nethermind.Evm;
using Nethermind.Int256;
using Nethermind.Logging;
using Nethermind.Serialization.Json;
using Nethermind.Specs.Forks;
using Nethermind.Specs.Test;
using Nethermind.Specs;
using Nethermind.State;
using Nethermind.Trie.Pruning;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System;

namespace Nethermind.Harness
{
    internal class Program
    {
        private static PrivateKey PrivateKeyD = new("0000000000000000000000000000000000000000000000000000001000000000");
        private static Address sender = new Address("0x59ede65f910076f60e07b2aeb189c72348525e72");

        private static Address to = new Address("0x000000000000000000000000636f6e7472616374");

_Trimmed to 38 lines — full report: https://notes.ethereum.org/qalqTnvEQkiFg6uTC20fWA_

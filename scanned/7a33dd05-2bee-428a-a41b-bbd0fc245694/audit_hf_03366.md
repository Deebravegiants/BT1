# [M] Incorrect emoji displaying

## Summary
Severity: Medium
Contest weight: 0.3632
Dataset id: 18247
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract generates an SVG image from a user‑provided biography string and splits the string into lines of 40 bytes before embedding it in the tokenURI metadata. The implementation assumes that a line break can be inserted after every 40 bytes without considering that many Unicode characters, especially emojis and composite flag symbols, occupy multiple bytes. The root cause is a simplistic byte‑based line‑splitting algorithm that only checks a limited set of continuation‑byte patterns and does not correctly handle grapheme clusters formed by sequences such as regional indicator symbols. When a multi‑byte emoji straddles a 40‑byte boundary, the algorithm may cut the emoji in half, treat the remaining bytes as a separate line, or skip them entirely. As a result, the generated SVG contains truncated or missing emoji glyphs, leading to an image that does not display the intended characters. From a user’s perspective the token’s visual representation may show a broken flag, missing symbols, or an empty space where the emoji should be, contradicting the expectation that the full biography, including all emojis, is rendered correctly. This defect can be exploited by an attacker who deliberately includes specially crafted emoji sequences in the bio field; the malformed SVG can cause UI rendering errors, break integrations that rely on the tokenURI, or obscure information in the metadata. The issue was discovered during a security audit when test cases containing a flag emoji composed of several code points produced an incorrectly split line and a malformed SVG. The problem is subtle because the tokenURI still returns a valid base64 JSON payload, so the error is only visible when the SVG is rendered, making it easy to overlook. To remediate the bug, the contract should avoid manual byte‑wise splitting and instead use a view function that constructs the SVG with proper Unicode‑aware line breaking, or store explicit byte offsets supplied by the caller to guarantee that line breaks occur only at safe boundaries. Implementing a Unicode‑compliant splitter or leveraging existing libraries to handle grapheme clusters will ensure that emojis are kept intact, preserving the visual integrity of the generated image and preventing integration failures.

## Proof of Concept
Let’s consider tokenURI function of the Bio contract.

Here implemented corner case for some emojis, but current implementation doesn’t handle all cases. I suppose handling all cases is redundant, erroneously, complicated and unnecessary.

Let’s consider part of tokenURI code in python, this part just rewritten on Python part of Solidity code:
    
    import binascii
    
    def sol_func_same(bio):
        bioTextBytes = str.encode(bio, "utf-8")
        lengthInBytes = len(bioTextBytes)
        lines = (lengthInBytes - 1) // 40 + 1
        strLines = [None for _ in range(lines)]
        prevByteWasContinuation = False
        insertedLines = 0
        bytesLines = []
        bytesOffset = 0
        for i in range(0, lengthInBytes):
            character = bioTextBytes[i]
            bytesLines.append(character)
            bytesOffset += 1
            if ((i > 0 and (i + 1) % 40 == 0) or prevByteWasContinuation or i == lengthInBytes - 1):
                nextCharacter = 0
                if (i != lengthInBytes - 1):  # 🏴󠁧󠁢󠁥󠁮󠁧󠁿
                    nextCharacter = bioTextBytes[i + 1]
                if (nextCharacter & 0xC0 == 0x80):
                    prevByteWasContinuation = True
                else:
                    if (
                            (nextCharacter == 0xE2 and bioTextBytes[i + 2] == 0x80 and bioTextBytes[i + 3] == 0x8D) or
                            (nextCharacter == 0xF0 and
                             bioTextBytes[i + 2] == 0x9F and
                             bioTextBytes[i + 3] == 0x8F and
                             int(bioTextBytes[i + 4]) >= 187 and
                             int(bioTextBytes[i + 4]) <= 191) or
                            (i >= 2 and
                             bioTextBytes[i - 2] == 0xE2 and
                             bioTextBytes[i - 1] == 0x80 and
                             bioTextBytes[i] == 0x8D)
                    ):
                        prevByteWasContinuation = True
                        continue
    
                    strLines[insertedLines] = binascii.unhexlify(''.join([hex(x)[2:] for x in bytesLines])).decode("utf-8")
                    insertedLines += 1
                    bytesLines = []
    
                    prevByteWasContinuation = False
                    bytesOffset = 0
    
        for idx, i in enumerate(strLines):
            print(idx, i)
    
    if __name__ == "__main__":
        sol_func_same("0🏴󠁧󠁢󠁥󠁮󠁧󠁿")
        print("===" * 20)
        sol_func_same("000000000000000000000000000000🏴󠁧󠁢󠁥󠁮󠁧󠁿")

The result is:
    
    0 0🏴󠁧󠁢󠁥󠁮󠁧󠁿
    ============================================================
    0 000000000000000000000000000000🏴󠁧󠁢
    1 󠁥󠁮󠁧󠁿

In the second line present 31 character.

but correct answer for the second case is:
    
    000000000000000000000000000000🏴󠁧󠁢󠁥󠁮󠁧󠁿

This happened because Eng flag presented with combination of different emojis, this case isn’t handled by contract.

Similar test might be added to the Bio.t.sol contract:
    
    function testSmallLine() public {
        string memory text = unicode"000🏴󠁧󠁢󠁥󠁮󠁧󠁿";
        bio.mint(text);
        string memory result = bio.tokenURI(1);
        console.logString(result);
    }
    
    function testLongLine() public {
        string memory text = unicode"000000000000000000000000000000🏴󠁧󠁢󠁥󠁮󠁧󠁿";
        bio.mint(text);
        string memory result = bio.tokenURI(1);
        console.logString(result);
    }

You need to decode them and you’ll receive the same incorrect result.

## Recommendation
Do not try to implement spec by themselves.

  1. Add view function which is responsible to create svg image. In tokenURI call this function to generate svg result.  
Like this:

    function generateSvg(string memory bioText) public view returns(string) {
        bytes memory bioTextBytes = bytes(bioText);
        uint lengthInBytes = bioTextBytes.length;
        // Insert a new line after 40 characters, taking into account unicode character
        uint lines = (lengthInBytes - 1) / 40 + 1;
    ...
    ...
    ...
        return string(abi.encodePacked("data:application/json;base64,", json));
    }

  2. Add possibility to manual split by lines. i.e. with bio additionally store offsets in bytes, by which lines must be split.

    function mint(string calldata _bio, uint256[] calldata byteSplit) external {
    ...
    }
    
    function generateSvg(string memory bioText, uint256[] memory byteSplit) public view returns(string) {
    ...
    bytes memory bioTextBytes = bytes(bioText);
    in for loop:
        slice = bioTextBytes[i:i+1]
        write slice to svg
    }

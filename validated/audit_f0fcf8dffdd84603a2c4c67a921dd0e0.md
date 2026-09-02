This is the key finding: the webhook `Request#to_signable_string` returns only `@raw_body` (the request body bytes), while `Request#shop` reads the `x-shopify-shop-domain` / `shopify-shop-domain` header directly, with no binding between the two.

### Title
Webhook shop identity (`x-shopify-shop-domain` header) is not covered by the HMAC signature, allowing shop spoofing on an otherwise-valid webhook - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header [1](#0-0) , but the HMAC signature it verifies (via `Utils::HmacValidator.validate`) is computed only over `to_signable_string`, which returns the raw body bytes and does not include the shop-domain header at all [2](#0-1) . This is the same class of bug as the report: a value that is *acted on* (`loanId` reused as a tenant/identity key) is not bound by the cryptographic check that is supposed to guarantee its integrity (the HMAC only signs the body, not the header carrying the shop identity).

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` value returned by the `VerifiableQuery` implementation [3](#0-2) . For `Webhooks::Request`, `hmac` is read from the `x-shopify-hmac-sha256` header and `to_signable_string` is just `@raw_body` [4](#0-3) . The `shop` accessor used by consumers of the request (e.g. `WebhookHandler#handle(topic:, shop:, body:)` implementations) is taken straight from the `x-shopify-shop-domain` header without any cryptographic linkage to the HMAC-covered body [1](#0-0) .

Because the app-level `api_secret_key` is shared across *all* shops that install the app, any webhook payload/HMAC pair that is valid for one merchant's webhook delivery remains cryptographically valid regardless of which `x-shopify-shop-domain` header value accompanies it — the header is never part of the signed material. This breaks the intended binding: `shop authenticated by HMAC == shop used to route/process the webhook`. In the loan-repayment analogy, `_loans[loanId]` (the value trusted for authorization) can be changed out from under the check (`_baseLoanChecks`) that is supposed to keep it consistent; here, the `shop` value trusted for tenant routing/authorization can be swapped out from under the HMAC check that is supposed to keep it consistent with the signed body.

### Impact Explanation
If an attacker can influence or replay the `x-shopify-shop-domain` header on a request that reaches the app's webhook endpoint while keeping a body/HMAC pair that is valid under the app's single shared secret (e.g., replaying/relaying a webhook originally sent for shop A, or racing header injection in a proxy/load-balancer misconfiguration in front of the app), the gem provides no defense: `validate` returns `true` and `Request#shop` will report whatever domain the header claims. Downstream app code that trusts `request.shop` to select the tenant's data/session (a common pattern per the `Webhooks::Registry`/`WebhookHandler` docs) can be misled into processing or attributing a webhook to the wrong merchant — a cross-tenant data integrity issue. This matches the report's core theme: a check exists (HMAC / `loanId` hash) but a related, security-relevant field (`shop-domain` / `loanId` binding) is not actually covered by that check.

### Likelihood Explanation
Exploitation still requires network-level ability to deliver a request with an attacker-chosen `x-shopify-shop-domain` header alongside a body/HMAC that validates — e.g., a compromised or misconfigured reverse proxy that lets `X-Shopify-Shop-Domain` be set by the client, or webhook replay across shops when infrastructure is shared. This is a design gap in the gem's own `VerifiableQuery` implementation for webhooks (no header binding), independent of any host-application misuse, and does not require possession of `api_secret_key`, an access token, or `client_secret`. Likelihood is moderate: it depends on how the host app's web server maps headers, but the gem provides zero cryptographic guarantee that `shop` correlates with the signed body.

### Recommendation
Include the shop-domain header (and ideally topic/webhook-id) in the HMAC-signed material, or independently verify that the `shop` header value matches an expected/allow-listed value tied to the session/store the webhook was registered for, before trusting `Request#shop` for any authorization or tenant-routing decision. At minimum, document that `Request#shop` is unauthenticated and must not be used as a security boundary.

### Proof of Concept
1. Register/simulate a webhook delivery where the app's secret is known to be shared across shops (standard Shopify app model).
2. Compute a valid HMAC for a given `raw_body` using the app's `api_secret_key` (as done in `test/webhooks/registry_test.rb` setup) [5](#0-4) .
3. Send that same `raw_body` + valid HMAC with an arbitrary `x-shopify-shop-domain` header value (e.g., `victim-shop.myshopify.com` instead of the originating shop).
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` never included the shop header [2](#0-1) , and `request.shop` returns the attacker-supplied domain [1](#0-0) , demonstrating the identity binding gap.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
```

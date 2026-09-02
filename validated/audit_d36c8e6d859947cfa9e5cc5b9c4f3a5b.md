### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header verbatim as the tenant identity handed to the app's handler. Because the signable string used for HMAC verification only contains the raw body, the `shop` field is not cryptographically bound to the signature, so it can be swapped independently while the HMAC still validates.

### Finding Description
`Webhooks::Registry.process` validates a webhook purely via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` as the tenant for dispatch: [1](#0-0) 

`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

For webhooks, `to_signable_string` returns only the raw JSON body — it does not include the `shop`, `topic`, `api_version`, or `webhook_id` headers: [3](#0-2) 

This is exactly the bug-class from the external report, transposed onto an identity-binding check: the report describes a system that acts on a set of resources (vaults) but fails to validate a precondition (paused state) for each one individually, causing unrelated state to leak into an operation it shouldn't affect. Here, the equivalent is: `shop` is a field *acted on* (used as the tenant key for dispatching webhook data to the host application's handler) but *not covered by the HMAC* that gates trust in the request. The equality that should hold is:

```
bytes_verified_by_HMAC == bytes_the_application_trusts_as_the_event's_identity
```

but instead:

```
bytes_verified_by_HMAC (raw_body only) != bytes_trusted_as_shop_identity (shop-domain header)
```

By comparison, the OAuth callback path (`Auth::Oauth::AuthQuery#to_signable_string`) correctly includes `shop` inside the signed content, so the two paths are inconsistent: [4](#0-3) 

The dispatched `WebhookMetadata` struct — which carries `shop` straight into the app's handler as the authoritative tenant — is built directly from `request.shop`: [5](#0-4) [6](#0-5) 

### Impact Explanation
Any actor who possesses one genuine `(raw_body, hmac)` pair (e.g., a legitimate webhook delivered for their own installed shop) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary value in the `shopify-shop-domain` (or `x-shopify-shop-domain`) header. `HmacValidator.validate` will still succeed because the header is outside the signed content, and the host application's handler receives `WebhookMetadata#shop` pointing at a shop the attacker does not control. Any host application that uses this gem's `shop` field as the tenant key to look up sessions, write records, or gate access (the documented and expected usage pattern) can be made to process/attribute attacker-controlled webhook payloads under another merchant's tenant — a cross-tenant data-integrity/confusion issue reachable without the `api_secret_key`.

### Likelihood Explanation
Medium-to-High: the attacker only needs to be a legitimate (even free/trial) installer of the app to obtain one valid signed webhook body/HMAC pair for their own shop, then can freely re-send that request with an altered `shop-domain` header value to the app's public webhook HTTP endpoint. No secret material, privileged account, or credential theft is required — only crafting an HTTP request, which is squarely within an "unprivileged internet user" capability once one legitimate payload has been observed.

### Recommendation
Bind `shop` (and ideally `topic`, `webhook_id`, `api_version`) into the HMAC-signed content used for webhook verification, or otherwise cryptographically tie the `shop-domain` header to the signature validation step, so that the HMAC also authenticates the request's claimed tenant identity, not just the body bytes. At minimum, document that host applications must independently re-verify `shop` against a known/installed-shop list before using it as a tenant key, since this gem does not bind it.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and receives a legitimate webhook call, capturing the raw body `B` and the valid header `shopify-hmac-sha256: H` (where `H = HMAC-SHA256(api_secret_key, B)`).
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `shopify-hmac-sha256: H` (unchanged, still valid since only body is signed)
   - Header `shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - Header `shopify-topic` / `shopify-webhook-id` set as desired (also unsigned).
3. `Webhooks::Request.new` accepts the forged headers, and `HmacValidator.validate` succeeds because `to_signable_string` only checks `raw_body` [7](#0-6) .
4. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the app's handler [6](#0-5) , causing the host application to process attacker-supplied data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

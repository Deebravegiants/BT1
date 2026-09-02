### Title
Webhook shop-tenant identity spoofing — the `Shopify-Shop-Domain` header is trusted for tenant identification but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
This is a valid analog to the reported bug class. The DAO report describes an identity binding that is broken: the record that gets acted upon (a DAO's chain identity) is not derived from, or verified against, a value that is actually authenticated. In `ShopifyAPI::Webhooks::Request`, the tenant identifier `shop` is read directly from the `Shopify-Shop-Domain`/`X-Shopify-Shop-Domain` HTTP header, but `to_signable_string` (the value that is HMAC-verified) is only the raw request body. The `shop` field that the registry uses to route/attribute the webhook to a specific merchant is never part of what is cryptographically bound by the signature.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [2](#0-1) 

For webhook requests, `to_signable_string` returns only the raw HTTP body: [3](#0-2) 

But `shop`, the value that the caller uses to know *which merchant this event belongs to*, is pulled straight from an HTTP header outside the signed payload: [4](#0-3) 

The binding that should hold is:
`hmac_verified_bytes == bytes_that_determine_the_tenant`

But in reality:
`hmac_verified_bytes == raw_body` while `tenant_used_by_app == headers["shopify-shop-domain"]`

These two are disjoint. `Registry.process` passes `request.shop` straight through to the handler as the authoritative tenant identifier: [5](#0-4) 

Because `shop-domain` is not part of the signed content, an unprivileged internet user who can obtain any single valid `(body, hmac)` pair from Shopify for topic X — e.g., by installing the app themselves on their own shop and capturing one legitimate webhook delivery for that topic, or from any other source of a valid signature/body pair for that same `client_secret`-signed payload shape — can resend that same body+hmac with an arbitrary `Shopify-Shop-Domain` header value. `HmacValidator.validate` will still succeed (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event is from the attacker-chosen shop.

This mirrors the DAO bug precisely: in the DAO case, the record's identity (its address) was not bound to the input that was supposed to make it unique per-chain, allowing an attacker to make the system believe a malicious record belonged to a victim's identity slot. Here, the webhook's tenant identity (`shop`) is not bound to the HMAC that is supposed to make the request trustworthy, allowing an attacker to make the host application believe an attacker-supplied/replayed event belongs to a different (or arbitrary) shop.

### Impact Explanation
This crosses the tenant boundary. Any app whose webhook handler uses `WebhookMetadata#shop` to decide which merchant's data/session/token to load or update (the officially documented and intended usage pattern of this field) can be made to attribute a webhook payload to the wrong (attacker-chosen) shop, since this gem itself performs no verification that `shop` corresponds to the entity that produced the signed body. This falls under cross-tenant access / credential or data misattribution.

### Likelihood Explanation
Medium. The attacker needs at least one valid `(raw_body, hmac)` pair — trivially obtainable by installing the target app in an attacker-controlled development store and letting Shopify deliver a real webhook for the topic they want to spoof (any account can create a dev/test store). No secret material is required; only the exact bytes+signature Shopify already sent are replayed with a substituted header value, which any client controlling the HTTP request to the app's webhook endpoint can do.

### Recommendation
Include the shop domain (and other Shopify-controlled webhook headers relevant to tenant/topic identity) in the HMAC-signed content, or otherwise cryptographically bind `shop` to the verified payload before it is used as a tenant identifier — for example, by validating it against the shop associated with the app's known/registered sessions, or by having `to_signable_string` incorporate the header value in a way Shopify also signs over. At minimum, document and enforce that consumers must independently corroborate `shop` (e.g., against an existing installed-shop record) before trusting it, since this gem does not verify it.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook for topic `orders/create`. They capture the raw request body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` that Shopify computed over `B` using the app's `client_secret`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256`: `H` (unchanged, still valid because it only signs the body)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (attacker-chosen, arbitrary)
3. `ShopifyAPI::Webhooks::Request.new` accepts this because all required headers are present.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `to_signable_string` (`= @raw_body`) against `H` — unaffected by the forged `shop-domain` header. [6](#0-5) 
5. The app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the event actually originated (per Shopify's real delivery) from `attacker-shop.myshopify.com`, causing the handler to act on/against the wrong tenant's data.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

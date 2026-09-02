### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop` (and `topic`/`webhook_id`/`api_version`) values taken from unauthenticated HTTP headers to route the payload to the host application's handler. Because the tenant-identifying field (`shop`) is not part of the signed data, the binding "HMAC-verified request == request attributed to shop X" does not hold, breaking the equality between *bytes verified* and *identity acted on*.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers without any cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body): [3](#0-2) 

`Registry.process` performs this HMAC check and then immediately forwards the unauthenticated `request.shop` value into the handler's data object, which host applications use to select/authenticate the tenant (e.g., load a session/store record for that shop): [4](#0-3) 

The identity equality the gem should guarantee is: *"the shop bound into the HMAC" == "the shop the handler acts on"*. Here it is instead: *"the shop parsed from an unauthenticated header" == "the shop the handler acts on"*, with the HMAC only proving *"these body bytes were signed by our secret at some point"* — not *"this specific shop sent this specific body."* Any attacker who is a merchant/unprivileged owner of any Shopify store (or who otherwise obtains one genuinely-signed webhook delivery, e.g. from a topic with static/predictable body content) can capture the valid `X-Shopify-Hmac-Sha256` value for that raw body and replay the request to the app's webhook endpoint with `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) rewritten to reference a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` dispatches the payload as if it originated from the victim tenant.

### Impact Explanation
This breaks the shop/tenant identity binding that host applications rely on to segregate per-merchant data (a documented usage pattern in `docs/usage/webhooks.md`, where `WebhookMetadata#shop` is the only tenant identifier surfaced to app code). An attacker can cause the app to process/attribute forged webhook events under another merchant's `shop` domain — a cross-tenant integrity/confidentiality issue that meets the Critical bar ("cross-tenant access") defined in the report scope, since the host application has no gem-provided means to detect that `shop` was not actually authenticated.

### Likelihood Explanation
The prerequisite is modest: the attacker only needs one instance of a genuinely HMAC-signed webhook body (trivially obtainable by installing the target app on their own, attacker-owned store — a normal unprivileged action — and capturing any webhook delivery, especially ones whose body content is static/predictable across shops, e.g., `app/uninstalled` bodies or topics with minimal/empty payloads). No access token, `client_secret`, or `api_secret_key` is required; only observation of one legitimate delivery to the attacker's own endpoint.

### Recommendation
- Short term: Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them to the signed payload), so tampering with these headers invalidates the signature.
- Long term: Document and enforce that host applications must never trust `WebhookMetadata#shop` without independently confirming it corresponds to a shop with an active app installation/session before performing tenant-scoped writes, and consider exposing a combined "verified shop" accessor from the gem itself rather than a bare header pass-through.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook delivery for a topic whose body is static/predictable (e.g., `app/uninstalled`), capturing the raw body `B` and its valid `X-Shopify-Hmac-Sha256: H` value.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because HMAC only covers body)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` optionally forged too
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
4. The app's registered handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed B, ...)` and performs tenant-scoped side effects under the victim's identity, even though the victim never sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

### Title
Webhook shop-domain header not covered by HMAC verification enables cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The `STORAGE QUERIES FILTER` report describes a case where a field used by downstream logic (`address`) is not properly bound by the packed/verified key, letting attacker-influenced bits leak into the "authenticated" value. The same class of bug exists in this gem's webhook processing: the HMAC signature only covers the webhook **body**, while the **shop identity** (`x-shopify-shop-domain` header) that the handler trusts as the tenant identifier is never included in, or independently validated against, that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop` is read straight from the (attacker-controllable, from-the-wire) header with no cross-check against the signed content: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC exclusively over `to_signable_string` (i.e., the body), never over the shop/topic/webhook-id headers: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` gates entirely on that body-only HMAC check, then forwards the *unverified* `request.shop` header value to the app's handler as the authenticated tenant: [4](#0-3) 

The identity binding that should hold is:
`HMAC(secret, signed_bytes) == received_hmac` should imply `signed_bytes` (and thus the shop context derived from them) belongs to the shop the app is told it belongs to. In this implementation, `signed_bytes` = raw body only, while the shop the handler ultimately trusts (`data.shop`, used for e.g. finding the merchant record to update) comes from a header entirely outside the signed bytes. Anyone who can obtain **any one** valid `(body, hmac)` pair for their **own** shop (trivial — they can install the app on their own store/dev shop and receive genuine webhooks for it) can replay that exact body+hmac pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. `Utils::HmacValidator.validate` still succeeds (body/hmac pair is authentic), and `Registry.process` calls the handler with `shop: <victim-shop>` and `body: <attacker's own shop's payload>` — a tenant-identity confusion.

### Impact Explanation
This allows cross-tenant data confusion: a webhook payload that is only legitimately associated with the attacker's own shop can be delivered to the app's handler tagged as belonging to a different (victim) shop. Depending on the handler's logic (e.g., updating records keyed by `shop`), this can lead to writing/attributing data to the wrong tenant, or triggering shop-specific side effects (e.g., uninstall/GDPR handlers, order/customer webhook handlers) for a shop the attacker does not control. This matches the "cross-tenant access" Critical-tier impact category, since the binding between the cryptographically verified payload and the tenant it is attributed to is broken.

### Likelihood Explanation
Exploitation requires no possession of `api_secret_key`, access tokens, or any privileged credential — only the ability to receive one legitimate webhook for a shop the attacker legitimately controls (any merchant/developer can install the app on a store they own) and the ability to POST an HTTP request with custom headers to the app's public webhook endpoint (which the app owner exposes to the internet by design, per `docs/usage/webhooks.md`). This is a realistic "unprivileged internet user" scenario reachable purely through documented use of the gem's `ShopifyAPI::Webhooks::Registry.process` API.

### Recommendation
Bind the shop (and, ideally, the topic/webhook-id) into the value that is HMAC-verified, or independently authenticate the shop header against the session/shop this delivery is expected for. Concretely:
- Include the `shop`, `topic`, and `webhook-id` header values in `to_signable_string` alongside the body, and verify the full concatenation.
- Alternatively, require handlers to look up/validate the shop domain against an app-controlled record (e.g., confirm this shop has an active, matching webhook registration) instead of trusting the header value implicitly at line `lib/shopify_api/webhooks/registry.rb:198`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery:
   - Headers: `x-shopify-hmac-sha256: <valid_hmac_for_body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, body: `{"id":1}`.
2. Attacker replays the exact same body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but changes the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC is only computed over the (unchanged) body — see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: {"id"=>1}, ...)` (`lib/shopify_api/webhooks/registry.rb:198`), causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

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

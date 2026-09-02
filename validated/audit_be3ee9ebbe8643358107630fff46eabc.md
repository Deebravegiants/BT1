### Title
Webhook shop-domain header is trusted for tenant identity without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` identity that the registry hands to the application's webhook handler comes from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, a field that is never included in the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: `to_signable_string` -> `@raw_body`. [1](#0-0) 

`Request#shop` is read straight from an HTTP header with no cryptographic tie to the body: [2](#0-1) 

`Registry.process` validates the HMAC over that body-only signable string via `Utils::HmacValidator.validate(request)`, and if it passes, immediately trusts `request.shop` as the tenant identity, forwarding it into the handler's metadata: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever checks `verifiable_query.to_signable_string` (the body) against the HMAC — the `shop` header plays no role in the signature computation: [4](#0-3) 

The broken identity binding, stated as an equality that the code fails to enforce:
`shop_that_the_HMAC_secret_actually_authorizes == shop_header_value_used_by_the_handler`

Since a merchant's app's `api_secret_key` is shared across every shop that installs that app (it is per-app, not per-shop), any party who legitimately receives one valid `(raw_body, hmac)` pair for a webhook belonging to their own shop can replay that exact body and signature to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a different shop that also has the same app installed. `Utils::HmacValidator.validate` will still succeed (it only checks the body bytes against the secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop, with body content fully chosen/controlled by the attacker (e.g. spoofing `app/uninstalled`, `shop/redact`, or `orders/create` payloads attributed to a shop the attacker does not own).

### Impact Explanation
This breaks the tenant boundary that webhook handlers rely on: the gem hands the application a `shop` value under a security guarantee ("this was validated") that does not actually hold, because the shop header is not part of the signed content. Any application logic that keys off `data.shop` (e.g. revoking a session, updating per-shop settings, deleting shop records on `shop/redact`, or writing attacker-controlled body data into another shop's records) can be tricked into acting on the wrong tenant using only a webhook body/signature the attacker previously legitimately received for their own shop. This matches the Critical "cross-tenant access" impact category, since no access token, `client_secret`, or privileged credential is needed — only a previously-seen valid webhook delivery for the attacker's own installation.

### Likelihood Explanation
Requires no privileged access: any unprivileged user who has installed the app on their own store (or captured one delivered webhook, e.g. via browser/network tooling or a proxy they control) obtains a valid `(body, hmac)` pair signed under the app's shared `api_secret_key`. They can then POST that body with the original HMAC header but an attacker-chosen `shopify-shop-domain` header to the app's public webhook endpoint. The only prerequisite is that the target app share the same webhook secret across shops (true for every standard, non-per-shop-secret Shopify app) and that the attacker be able to trigger at least one webhook for their own shop with body content useful for the target topic.

### Recommendation
Do not treat the `shop` header as trusted merely because the body's HMAC validates. Bind the `shop` value into the same integrity check, e.g. by looking up the caller's session/shop-scoped secret, or by cross-checking `shop` against a value embedded in and covered by the signed payload (or against server-side knowledge of which shop the webhook subscription belongs to, keyed by `webhook_id` from Shopify's own records) before trusting `request.shop` as a tenant identifier in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the exact same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` and succeeds, since `B` and `H` are untouched.
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the application to process attacker-supplied data as though it came from `victim.myshopify.com`.

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

### Title
Webhook `shop` (and `topic`/`webhook-id`) header values are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable payload only from the raw HTTP body, while the shop domain, topic, and webhook id are read straight out of unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC of the body and then forwards the header-derived `shop` value, unauthenticated, to the app's webhook handler. This breaks the intended binding: `hmac(raw_body) == valid` should imply `shop-domain == the shop that produced raw_body`, but the gem never establishes that equality.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are pulled from HTTP headers with no cryptographic relationship to the signed body: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` when constructing the metadata handed to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` (called from `process`) only ever verifies `verifiable_query.to_signable_string`, i.e. the raw body, never the headers: [4](#0-3) 

Because Shopify signs webhooks with the app's single, app-wide `client_secret` (not a per-shop secret), any merchant who has installed the app receives genuinely-signed webhook deliveries for their own shop. That merchant (an "unprivileged" actor relative to other tenants of the same app) can capture a `(raw_body, hmac)` pair from their own legitimate webhook and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header rewritten to name a different shop. `HmacValidator.validate` still returns `true` because it only checks the untouched body against the correct secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop, with the attacker's chosen body content.

This is precisely the "field acted on but not covered by the HMAC" identity-binding break called out in scope: the shop identity that the handler is meant to trust is not the shop identity that was cryptographically verified.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` (the gem's documented, intended API) to decide which tenant's data to update, delete, or read will process attacker-controlled data under another merchant's identity. This is a cross-tenant integrity/data confusion issue: an attacker who is a legitimate (but unprivileged, non-victim) merchant of the app can inject fabricated webhook events attributed to a shop they do not control, potentially triggering data corruption, unauthorized state changes, or information disclosure keyed by the spoofed shop. This matches the "cross-tenant access" high/critical impact category, since the boundary crossed is the per-merchant tenant boundary that the gem's webhook API is supposed to enforce.

### Likelihood Explanation
Likelihood is realistic given the boundary crossed: it requires no leaked secret, no privileged account, and no protocol confusion beyond installing the app once as any shop and then replaying a captured payload with a modified header to the same public webhook endpoint. It does require knowledge of the app's public webhook URL and one legitimate installation, both of which are attainable by an ordinary app user.

### Recommendation
Bind the header-derived identity fields into the signed material that `HmacValidator` checks, e.g. by including `shop-domain`, `topic`, and `webhook-id` in `to_signable_string` (or by requiring the host app to independently verify `shop` against a known/expected value before trusting `WebhookMetadata#shop`), and document this as a hard requirement rather than leaving it implicit in `Request`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`) delivered with a valid `X-Shopify-Hmac-Sha256` computed by Shopify using the app's shared `client_secret`.
2. Attacker captures the exact `raw_body` and `X-Shopify-Hmac-Sha256` value from that delivery.
3. Attacker POSTs the same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (via `Registry.process`) succeeds because it only checks `raw_body` against the secret; `WebhookMetadata.shop` is now `"victim-shop.myshopify.com"`, so the app's handler acts on the attacker's payload as though it originated from the victim shop. [3](#0-2)

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

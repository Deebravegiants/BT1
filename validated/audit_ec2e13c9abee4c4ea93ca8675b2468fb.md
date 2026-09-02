### Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its `to_signable_string` (the value the HMAC is verified against) from only the raw request body, while the `shop`, `topic`, and `webhook_id` values that `ShopifyAPI::Webhooks::Registry.process` uses to route and label the event are read from separate, unauthenticated HTTP headers that are never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id`, however, are pulled directly from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC solely against `verifiable_query.to_signable_string`: [3](#0-2) 

`Webhooks::Registry.process` trusts `request.shop` and `request.topic` for dispatch and hands them straight to the app's handler once the (body-only) HMAC check passes: [4](#0-3) 

The identity binding that should hold is: `shop` (used by the host app to select a tenant/session and process the event) **==** `shop` that was actually authenticated by the HMAC. Because `to_signable_string` only covers `@raw_body`, this equality is never enforced — `hmac == HMAC(secret, body)` but `shop`, `topic`, and `webhook_id` are unauthenticated headers that can be swapped independently of the signed body.

Concretely, if an attacker (who legitimately operates their own shop and therefore receives real, correctly-signed webhook deliveries to their own endpoint, or who can otherwise capture a valid `body + hmac` pair, e.g. a shop with identical/predictable body content such as `{}` or a fixed test payload as seen in the maintainers' own test fixtures) resends the same body and hmac to the app's shared webhook endpoint but substitutes the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic` / `X-Shopify-Webhook-Id`) header with another shop's domain, the HMAC check in `HmacValidator.validate` still passes because it never inspected those headers. `Registry.process` then invokes the topic handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is the attacker-controlled value, causing the host application to act as though the event originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the HMAC is supposed to provide: verified bytes (the body) are decoupled from the acted-upon identity (`shop`/`topic`/`webhook_id`). Any application logic that uses `WebhookMetadata#shop` to select a session, update per-shop state, or gate an action can be tricked into cross-tenant processing — e.g., processing a spoofed `app/uninstalled`, `shop/update`, or other event as if it belongs to a different merchant, or misattributing webhook data across tenants. This matches the "Critical - cross-tenant access" impact category since it lets one shop's traffic be relabeled as another shop's identity without possessing that shop's secret.

### Likelihood Explanation
Exploitability requires the attacker to already have at least one validly-signed `(raw_body, hmac)` pair — which any merchant/app-installer legitimately receives for their own shop's webhooks, or which is trivial when the body is fixed/predictable content (several official Shopify webhook payloads for a given topic can be near-identical across shops, e.g. empty `{}` bodies or otherwise repeatable structures, as reflected even in this gem's own test fixtures using `"{}"` bodies). No possession of the app's `client_secret` or `api_secret_key` is needed to forge the *shop identity* — only to forge the body signature, which the attacker doesn't need to forge because they replay an already-valid signature.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or equivalent) in the signed/verified material for webhooks, or otherwise cryptographically bind them to the payload before trusting them for dispatch. If Shopify's webhook HMAC scheme is defined to only ever cover the body (per Shopify's actual webhook spec), then `ShopifyAPI::Webhooks::Registry` should not treat header-derived `shop`/`topic` as authenticated identity for cross-tenant-sensitive operations without an additional binding (e.g., cross-checking `shop` against the topic/subscription that was registered, or validating the webhook against a known set of subscribed shop domains) rather than passing them through unchecked to the handler as trusted metadata.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery with body `{}` for topic `orders/create`, along with a valid `X-Shopify-Hmac-Sha256` header computed as `HMAC-SHA256(api_secret_key, "{}")`.
2. Attacker resends this exact `raw_body` and `hmac` to the app's public webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and/or a different `X-Shopify-Webhook-Id`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, and `hmac` is computed from `Digest.hexencode(Base64.decode64(...))`; `to_signable_string` returns just `raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`).
4. `HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, "{}")` and compares it to the attacker-supplied hmac — it matches because `secret` and `body` are unchanged (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` proceeds, calling the app's handler with `shop: "victim.myshopify.com"` even though the request never originated from Shopify for that shop (`lib/shopify_api/webhooks/registry.rb:188-200`).

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

Confirmed: the webhook `shop` (tenant identity), `topic`, `api_version`, and `webhook_id` are all read from HTTP headers via `shopify_header` in `lib/shopify_api/webhooks/request.rb`, none of which are covered by `to_signable_string`, which returns only `@raw_body`. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body alone and then dispatches `request.shop` directly to the app's handler.

### Title
Webhook `shop` (tenant) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable content as the raw request body only, while the tenant-identifying `shop-domain` header (along with `topic`, `api-version`, and `webhook-id`) is read separately and is never included in the signed bytes. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identity for the webhook handler without it being bound to the HMAC that "authenticates" the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`hmac` and `shop` are both derived from unauthenticated HTTP headers via `shopify_header`: [2](#0-1) 

`Utils::HmacValidator.validate` computes the expected signature purely from `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC and, once it passes, unconditionally trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` as the identity of the event, dispatching them to the registered handler: [4](#0-3) 

The identity binding that should hold is: `hmac` authenticates `(shop, topic, body)` as one unit — i.e. `verified(shop) == shop_dispatched_to_handler`. Instead, only `verified(body) == body`, while `shop` is accepted from a header with no cryptographic tie to the signature. Since the app's `api_secret_key` is the same across every shop installed on the app, any party who can obtain one valid `(raw_body, hmac)` pair — for example, from their own store's legitimate webhook delivery, or any webhook they can trigger for a shop they control — can resend the identical body and HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because the body bytes are unchanged, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` where `shop` is the attacker-chosen value.

### Impact Explanation
This breaks the shop/tenant authentication boundary the HMAC is meant to provide: an app relying on `data.shop` (as the docs at `docs/usage/webhooks.md` explicitly recommend: `puts "... shop: #{data.shop} ..."`) to route or attribute webhook data per-tenant can be made to ingest or act on forged data under a victim shop's identity — a cross-tenant data injection/confusion vulnerability, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitability only requires an unprivileged attacker who can trigger at least one legitimate webhook for any shop (including a shop they control themselves, e.g., a free development store) to capture a valid `(body, hmac)` pair, then replay it against the target app's public webhook endpoint with a spoofed `shopify-shop-domain` header. No access token, `client_secret`, or privileged account is required.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the verified signature material, or independently verify that the `shopify-shop-domain` header corresponds to a shop with an active session/installation known to the app before trusting it, rather than trusting the header value merely because the body-only HMAC validated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` (or otherwise triggers one legitimate webhook delivery) and captures a legitimate webhook POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(secret, B)`), along with `X-Shopify-Topic` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (leaving `B` and `H` untouched).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim-shop.myshopify.com", "shopify-hmac-sha256" => H, ...})` is constructed and passed to `ShopifyAPI::Webhooks::Registry.process`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)` and finds it equal to `H`, returning `true` since `to_signable_string` never included the shop header — see `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: JSON.parse(B), ...)`, causing the app to process attacker-controlled body content as if it were authentically produced/authorized for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

Found it: the webhook `Registry.process` verifies the HMAC over the raw request body only, but the `shop` field consumed by the handler comes from an HTTP header (`shopify-shop-domain`) that is not covered by the HMAC signature at all.

### Title
Webhook shop identity spoofing via unsigned `shopify-shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` in `Registry.process` only authenticates the raw JSON body bytes, never the `shop` value [2](#0-1) . The `shop` accessor is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is completely outside the HMAC coverage [3](#0-2) . `Registry.process` passes this unauthenticated `request.shop` straight into `WebhookMetadata` and into the app's `handler.handle` call [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop value trusted by the handler == shop value cryptographically bound into the signed payload`. Here that equality is broken: `hmac == HMAC(secret, raw_body)` binds only the body, while `shop == header["shopify-shop-domain"]` is taken from a header never included in `to_signable_string`. An attacker who has captured (or replayed) any single valid webhook delivery for their own shop — a legitimately signed body along with its valid HMAC, which any shop owner can obtain simply by installing the app on their own store and receiving a real webhook — can resend that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting a different value in the `shopify-shop-domain` header. Since `HmacValidator.validate` only recomputes the signature over `@raw_body`, and the header is not part of the signable string, the HMAC still validates successfully with the tampered shop header. The application then dispatches the webhook `handler.handle` with a `WebhookMetadata` claiming to be from an arbitrary shop of the attacker's choosing, causing cross-tenant data confusion in any host application that relies on this gem's `Registry.process`/`WebhookMetadata#shop` to identify which merchant's data to update.

### Impact Explanation
This breaks the shop-tenant identity binding that webhook consumers rely on. An attacker-controlled `shop` value reaching the handler's business logic (e.g., writing order/customer data, deleting data, updating settings) for a shop they don't own constitutes cross-tenant access — one of the explicitly accepted Critical impacts.

### Likelihood Explanation
Likelihood is Medium: exploitation requires the attacker to first obtain one genuinely signed webhook body+HMAC pair, which is trivially available to anyone who installs the app on their own (attacker-controlled) shop — no privileged credentials or secret key needed, satisfying the "unprivileged internet user" constraint.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`/`api_version`) in the value that is HMAC-verified, or independently validate that the `shopify-shop-domain` header matches metadata already bound to the raw body (e.g., a `shop` claim embedded in the payload signed by Shopify), rather than trusting an unauthenticated header for tenant identification. At minimum, document that `WebhookMetadata#shop` is unauthenticated so host applications don't use it as an authoritative tenant key.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger any topic (e.g., `orders/create`) to receive a legitimately signed webhook: raw body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B`), header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Replay the exact same `B` and `H` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` decodes `H` unchanged; `to_signable_string` returns `B` unchanged [5](#0-4) .
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` and succeeds because the shop header was never part of the signed content [6](#0-5) .
5. `Registry.process` calls `handler.handle` with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed body of the attacker's own order, ...)` [7](#0-6) , causing the host app to attribute the attacker's data to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

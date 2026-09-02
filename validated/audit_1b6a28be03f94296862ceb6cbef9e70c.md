### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop` (tenant) identifier is read from the unauthenticated `X-Shopify-Shop-Domain` header. `Webhooks::Registry.process` verifies the HMAC and then forwards `request.shop` straight into `WebhookMetadata`, which host applications use to attribute the webhook to a merchant/tenant. Because the header is not part of the signed bytes, an attacker who possesses one valid `(body, hmac)` pair can freely rewrite the `shop-domain` header and have the webhook accepted as coming from a different shop.

### Finding Description
`to_signable_string` returns only the raw request body: [1](#0-0) 

`shop` is read independently from a header that is never fed into the HMAC computation: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the body), never against `shop`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorizing the whole `Request`, including `request.shop`, and hands it to the app's handler as the authoritative tenant identity: [4](#0-3) 

The broken identity binding, expressed as an equality that the gem fails to enforce:

`HMAC_valid(raw_body, client_secret) == true` should imply `shop == the tenant that actually generated raw_body`, but the gem only proves the first clause. `shop` is parsed from headers outside the signed byte range, so `bytes_verified (raw_body) != bytes_used_for_tenant_routing (shop header)`.

Because Shopify signs *all* webhooks for a given app with the same `client_secret` (the HMAC does not encode which shop sent it), any shop that has installed the app can legitimately obtain a `(raw_body, hmac)` pair that is valid for the app's secret. That pair can then be replayed with the `X-Shopify-Shop-Domain` header rewritten to name a different, victim shop. `HmacValidator.validate` will still return `true` since the signed bytes (`raw_body`) and secret are unchanged, and `Registry.process` will hand `WebhookMetadata.shop == victim_shop` to the host app's handler.

### Impact Explanation
This breaks the tenant/session boundary this gem is responsible for asserting: the `shop` value returned by `Webhooks::Request`/`WebhookMetadata` is the field host applications rely on to select the correct merchant session/store data before acting on the webhook body. An attacker who is a legitimate merchant of the target app (i.e., can trigger any webhook for their own shop, e.g. `orders/create`) can forge that same request as if it originated from an arbitrary victim shop, causing the host application to process attacker-controlled body content under another tenant's identity — a cross-tenant data/action confusion rooted entirely in this gem's `Request`/`Registry` implementation, not in host misuse.

### Likelihood Explanation
Any merchant who installs the app can generate a valid `(body, hmac)` pair for their own shop's webhooks trivially (e.g. by placing an order, editing a product, etc., or replaying a captured delivery), then POST it to the app's webhook endpoint with a different `shop-domain` header. No access to `client_secret`, access tokens, or the Shopify signing key is required — only the ability to trigger one webhook delivery to oneself and resend it with a modified header, which is straightforward for any installer of the app.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is actually verified, not just the raw body. In `lib/shopify_api/webhooks/request.rb`, include the `shopify-shop-domain` (and `topic`) header content as part of `to_signable_string`, or otherwise re-derive the shop for the handler dispatch from `client_secret`-scoped context rather than trusting an unauthenticated header field. At minimum, document/enforce that `Registry.process`/`WebhookMetadata.shop` must be cross-checked by the host app against the shop associated with the specific webhook subscription (e.g. by verifying the calling `webhook_id` belongs to that shop) before it is trusted as a tenant key.

### Proof of Concept
1. App merchant A installs the app and triggers any subscribed webhook (e.g. `orders/create`), capturing the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because Shopify computed `H = HMAC(client_secret, B)`).
2. Merchant A replays this exact request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` from `merchant-a.myshopify.com` to `victim-shop.myshopify.com`.
3. `Webhooks::Request#hmac` reads the (unchanged) `X-Shopify-Hmac-Sha256` header; `#to_signable_string` returns the unchanged body `B`. [5](#0-4) 
4. `HmacValidator.validate` recomputes `HMAC(client_secret, B)`, which still equals `H`, so validation passes. [6](#0-5) 
5. `Registry.process` accepts the request and calls the handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now returns `"victim-shop.myshopify.com"`. [7](#0-6) 
6. The host app's handler processes attacker-controlled webhook content believing it is authoritative data from `victim-shop`, e.g. updating cached data, triggering side effects, or logging actions attributed to the victim tenant.

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

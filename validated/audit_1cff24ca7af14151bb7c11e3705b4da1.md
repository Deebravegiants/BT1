### Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Forgery - ([File: lib/shopify_api/webhooks/request.rb](), [File: lib/shopify_api/webhooks/registry.rb]())

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while `Registry.process` trusts the unauthenticated `shop-domain` header to identify which tenant a webhook belongs to. Because the app's `api_secret_key` is identical for every shop that installs the app, an attacker who legitimately receives one valid signed webhook (e.g., for their own store) can resend the exact same body/HMAC pair while substituting a different shop's domain in the header, and the library will accept it as authentic for that other shop.

### Finding Description
`HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the received signature: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw request body — none of the Shopify-supplied headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) are included in the signed material: [2](#0-1) 

Yet `shop` is read straight from the unauthenticated header: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards `request.shop` (the unauthenticated header value) as the tenant identity to the app's webhook handler, with no cross-check that the signed body actually corresponds to that shop: [4](#0-3) 

This breaks the identity binding: `shop authenticated` (i.e., the value the HMAC check implicitly vouches for — which is nothing, since `shop` isn't part of the signed string) `≠ shop used to route/process the event` (the raw header value passed into `WebhookMetadata`). Since `api_secret_key` is shared across every shop installing the app, any tenant who can obtain one legitimately signed webhook (from their own shop, which they control) can replay that same body+HMAC pair against the app's webhook endpoint with a different `shop-domain` header, and `HmacValidator.validate` will still return `true` because it never examines the header at all.

### Impact Explanation
This is a cross-tenant access vector: the webhook handler in the host app receives `WebhookMetadata` claiming to be from shop B while the payload was actually signed for shop A. Any app logic that uses `data.shop` to look up/write per-tenant records (a documented and expected pattern — `WebhookMetadata` exposes `shop` precisely for this purpose) can be tricked into applying attacker-controlled webhook data under a victim shop's identity, corrupting or exposing cross-tenant state without ever compromising the victim's credentials.

### Likelihood Explanation
Exploitation requires only that the attacker control one shop that has the app installed (a normal, unprivileged position for any internet user who installs a public app) and can capture one webhook delivery for that shop — trivial since the attacker owns that shop's endpoint. No access token, `client_secret`, or victim credential is required; only the ability to replay an HTTP POST with a modified header to the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the signed material or otherwise cryptographically tie the `shop-domain` header to the verified payload — e.g., include the shop domain (and ideally `topic`/`webhook-id`) in `to_signable_string`, or independently verify the shop against out-of-band webhook registration metadata (webhook ID lookup per shop) before dispatching to the handler. At minimum, document that `WebhookMetadata#shop` is not cryptographically authenticated and must not be trusted for tenant-scoping without additional verification.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the shared `api_secret_key`), header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body `B` and HMAC header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H`, per `lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb#to_signable_string`.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

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

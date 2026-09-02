### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` (merchant identity) used to route and process the webhook is read from an unsigned HTTP header. Any party who possesses one valid `(raw_body, hmac)` pair for their own shop can replay that exact pair while substituting a different `X-Shopify-Shop-Domain` header value, and the gem's `HmacValidator` will accept it as authentic — attributing the webhook to a different tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But the shop identity used downstream comes from a header that is never part of the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC over the `Request` object and then immediately trusts `request.shop` (the unsigned header) as the tenant identity passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, so it never incorporates `shop-domain`, `topic`, `webhook-id`, or `api-version`: [4](#0-3) 

Because every shop installing the same app shares the same signing secret (`Context.api_secret_key`/`client_secret`), a webhook body+HMAC pair that is valid for Shop A is *also* a valid HMAC for the identical body when replayed with Shop B's (or any attacker-chosen) `X-Shopify-Shop-Domain` header — the signature check only verifies the body was signed by "some shop using this app," not which shop. This breaks the equality that should hold: `shop authenticated by HMAC == shop used to identify the tenant in WebhookMetadata`. Here, the shop bound into `WebhookMetadata` comes from parsed-but-unauthenticated header bytes, not from the HMAC-covered payload.

### Impact Explanation
An attacker who is an installed merchant of the target app (or otherwise observes/replays a legitimately delivered webhook, e.g. via network capture or a compromised low-trust channel) can forge a request to the app's webhook endpoint with the original valid body/HMAC but an arbitrary `shop-domain` header. Because `Registry.process` only checks `Utils::HmacValidator.validate(request)` (body-only) before dispatching `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))`, the app-level handler will process attacker-controlled/replayed data under a spoofed tenant identity. This is a cross-tenant data-integrity issue: the app can be made to apply Shop A's webhook payload (e.g. order, product, GDPR redact events) to Shop B's records, since the HMAC never binds the payload to the claimed shop.

### Likelihood Explanation
Any party that has legitimately received one webhook for their own shop (a low-privileged, unauthenticated-relative-to-other-tenants position) has everything needed: a valid `raw_body` + `hmac-sha256` pair. They only need to change the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header value when POSTing to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or other shops' secrets is required, satisfying the "unprivileged internet user" analog required for this scan.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signed material, or explicitly cross-check the value of `X-Shopify-Shop-Domain` against a shop your integration expects/has an active session for before trusting it as the tenant identity. At minimum, document that `request.shop` is not authenticated by the HMAC and must not be used as a sole tenant-binding key; downstream consumers should validate it against the shop associated with the session/store they expect to receive webhooks from.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com`. Shopify delivers a legitimate webhook to the app's endpoint with headers:
   `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-raw-body>`, and some `raw_body`.
2. Attacker (who controls or observes this request, e.g. is themselves the merchant of `shop-a`) resends the same `raw_body` and same `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a `Request` whose `to_signable_string` is unchanged (`raw_body` only).
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC purely from `raw_body` and matches successfully, since the header change never affected the signed input.
5. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop == "shop-b.myshopify.com"`, causing the app to process Shop A's payload as if it belonged to Shop B.

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

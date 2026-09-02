## Title
Webhook HMAC covers only the raw body, not the `shop-domain` header — cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs (for HMAC verification purposes) only the raw request body via `to_signable_string`, while the `shop` identifier that `ShopifyAPI::Webhooks::Registry.process` hands to the host application's handler is read directly from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` header. The HMAC never binds the header to the body, so the two values can be recombined by an attacker who is a legitimate merchant on the same app.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the incoming header with no cross-check against the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC produced from `to_signable_string` (i.e. the body), then forwards `request.shop` — the unauthenticated header value — to the app's webhook handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field — again, purely a function of the body, independent of `shop`: [4](#0-3) 

Because the `api_secret_key` (the app's client secret) is shared across **every** shop that installs the app, any unprivileged merchant who installs the app on their own store receives genuine webhooks whose `(raw_body, hmac)` pair validates successfully under this scheme regardless of which shop domain accompanies them. That merchant can capture one such valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header (e.g. a victim shop's domain). `HmacValidator.validate` still returns `true` because it never inspects `shop`, and `Registry.process` passes the attacker-chosen `shop` value straight to the handler as if Shopify had certified it.

The broken identity binding, stated as an equality that should hold but doesn't:
`shop_bound_by_hmac == shop_used_by_handler` is false — the gem verifies `body` but the host application acts on `shop`, a field the HMAC never covers.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (as returned by `Registry.process`) to select which merchant's records to create/update/delete — which is the documented, expected usage pattern shown in this gem's own webhook docs/tests — can be made to attribute attacker-supplied webhook data to an arbitrary victim shop. This is a cross-tenant data/state confusion primitive: an unprivileged internet user (any merchant who can install the public app) can inject data under another tenant's identity without ever obtaining that tenant's access token or credentials.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on a shop of their own (the normal, unprivileged path for any public Shopify app) and be able to POST arbitrary HTTP requests to the app's public webhook endpoint with a spoofed `X-Shopify-Shop-Domain` header — both trivially available to any internet user, no leaked secrets or privileged account needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-verified signable content, or otherwise have `ShopifyAPI::Webhooks::Request#to_signable_string` incorporate the shop domain so that `HmacValidator.validate` fails if the header is altered independently of the body. At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is unauthenticated header data and must be independently validated by host applications (e.g., checked against a shop for which the app holds an active, previously-stored session) before being trusted as a tenant identifier.

### Proof of Concept
1. Install the target public app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the legitimate `raw_body` and `X-Shopify-Hmac-Sha256` value Shopify sends.
2. POST the same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, raw_body)` — unaffected by the header change — and passes validation: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, and — following this gem's documented usage — the host application processes/stores this data under the victim tenant.

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

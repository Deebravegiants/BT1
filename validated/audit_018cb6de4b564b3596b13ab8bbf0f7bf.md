### Title
Webhook `shop` (and topic/webhook-id) identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the tenant-identifying `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then dispatches the handler using these unbound header values, so the authenticated bytes (body) and the acted-upon identity (shop) are different objects — exactly the "bytes verified versus bytes parsed" binding break called out in scope.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate`, which only checks the body/secret HMAC via `validate_signature`: [3](#0-2) 

After that single check passes, the registry immediately dispatches to the handler using the unauthenticated `shop`/`topic`/`webhook_id` values: [4](#0-3) 

Because `Context.api_secret_key` is a single shared secret for the whole app across **all** installed shops (not per-tenant), any merchant who has installed the app can legitimately trigger a webhook to their own store, observe a valid `(raw_body, hmac)` pair for a known/predictable body, and then replay that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) headers to name a *different* victim shop. `HmacValidator.validate` will still pass because it only checks that the body was signed with the app's secret — which it was, just not necessarily for the claimed shop. The handler then executes under `WebhookMetadata` built entirely from the attacker-supplied headers.

### Impact Explanation
This breaks the binding: `shop authenticated == shop actually claimed`. Any app that uses `WebhookMetadata#shop` to key its data store, apply merchant-specific business logic, or write into another tenant's records is exposed to cross-tenant data corruption/impersonation — an unprivileged internet user who is merely a legitimate merchant of the same app can forge events attributed to a different merchant's shop. This matches the in-scope "cross-tenant access" Critical impact category, since the shop-domain identity used to route/act on webhook data is not bound to the authenticated payload.

### Likelihood Explanation
Any user who can install the app on a shop they control (a normal, unprivileged onboarding flow, not requiring `api_secret_key` or any special privilege) can capture one valid `(body, hmac)` pair for a predictable/empty body (e.g., `{}` or any topic whose payload the attacker controls) and replay it against the app's public webhook endpoint with forged shop/topic headers. No TLS interception, leaked credentials, or privileged access is required — only a free merchant account on the app, which is the baseline unprivileged-internet-user capability.

### Recommendation
Bind the trusted request metadata into the HMAC-signable material (or otherwise cryptographically bind `shop`/`topic`/`webhook_id` to the payload), and/or independently verify that the `shop` header corresponds to a shop that actually has this webhook/topic/id registered before dispatching to the handler, instead of trusting header values once the body-only HMAC passes.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook whose body is empty/predictable, e.g. `{}` for a topic the app subscribes to.
2. Capture the resulting `X-Shopify-Hmac-Sha256` value for body `"{}"` — this is valid for *any* shop of this app, since `HmacValidator.validate` only checks `OpenSSL::HMAC.hexdigest(sha256, Context.api_secret_key, "{}")`, as seen in: [5](#0-4) 
3. POST directly to the app's webhook endpoint with the same body `"{}"` and captured HMAC, but set `X-Shopify-Shop-Domain: victim.myshopify.com` and any desired `X-Shopify-Topic`/`X-Shopify-Webhook-Id`.
4. `Registry.process` accepts the request (HMAC over body matches) and calls the registered handler with `WebhookMetadata.new(topic: "victim's topic", shop: "victim.myshopify.com", body: {}, ...)`, causing the app to execute tenant-specific logic for `victim.myshopify.com` triggered entirely by the attacker.

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

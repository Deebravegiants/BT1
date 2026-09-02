### Title
Webhook shop identity confusion via unauthenticated `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers that are never included in the HMAC computation. `Registry.process` validates the HMAC against the body and then forwards the unauthenticated `shop` header value straight into `WebhookMetadata`, which the host app's handler uses as the tenant identity for the event.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all derived from headers that are excluded from the signable string: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` when building the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

This breaks the identity binding `shop authenticated == shop stored/acted-on`: the HMAC only proves the body byte sequence was signed with the app's `client_secret` for *some* delivery — it proves nothing about which shop that delivery is for. `shop`, `topic`, and `webhook_id` are attacker-controllable header bytes with no cryptographic tie to the signed body. `Utils::HmacValidator.validate` confirms this — it only ever calls `verifiable_query.to_signable_string`, which for `Request` is the body: [4](#0-3) 

### Impact Explanation
Because a single app-level `client_secret` signs webhooks for every shop that installs the app, any merchant who installs the app can legitimately receive a validly-HMAC'd `(body, hmac)` pair for their own shop. That pair can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header rewritten to name a different, victim shop. `Registry.process` will still consider the HMAC valid (it only checks the body) and will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop. Any host application that uses `data.shop` from the handler as the tenant key (e.g., to look up/update per-shop state, apply mandatory-topic actions like `customers/redact`, or route business logic) can be tricked into acting on the wrong tenant — a cross-tenant data/action confusion driven entirely by unauthenticated header bytes that this gem itself never binds to the signature. This maps to the "field acted on but not covered by the HMAC" analog class called out in scope.

### Likelihood Explanation
Requires only that the attacker (1) be able to install the target app on their own shop (or otherwise obtain one valid signed webhook body) and (2) send an HTTP POST to the app's public webhook endpoint with forged headers — no access token, `client_secret`, or privileged access is needed. This is a realistic unprivileged-internet-user path against the gem's own webhook-processing code.

### Recommendation
Bind the shop (and ideally topic/webhook-id) identity into the HMAC verification path — e.g., have `Registry.process` cross-check `request.shop` against an independently-established tenant context (such as the session/shop the endpoint is registered for) rather than trusting the header value implicitly, or document/enforce that host applications must never treat `WebhookMetadata#shop` as authenticated without separate verification. At minimum, the gem's documentation and `WebhookMetadata` should make explicit that `shop`, `topic`, and `webhook_id` are NOT covered by the HMAC signature.

### Proof of Concept
1. Attacker installs the target Shopify app on shop `attacker.myshopify.com` and receives a real webhook (e.g., `orders/create`) with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared `client_secret`.
2. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id` if the target topic's body shape matches).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unmodified) body. [5](#0-4) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload/signature actually originated from `attacker.myshopify.com`'s install, causing the host app to act on/behalf of the wrong tenant.

Note: I could not locate `lib/shopify_api/webhooks/webhook_metadata.rb` in the indexed codebase (glob search returned no results), so I could not verify field-by-field how `WebhookMetadata` is consumed downstream beyond the constructor call shown in `registry.rb`. This may be due to index size limits — a Devin session with full repo access could confirm the exact `WebhookMetadata` definition and any additional downstream validation that might exist there.

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

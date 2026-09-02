### Title
Webhook `shop` Attribution Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` documents that it "will verify the request did indeed come from Shopify" before dispatching `data.shop` (described as "The shop domain of the webhook") to the app's handler. In reality, `Utils::HmacValidator` only authenticates the raw body; the `shop` value delivered to the handler is read from an unauthenticated header, breaking the intended binding between "authenticated webhook" and "the shop it is attributed to."

### Finding Description
`Registry.process` first validates the request, then builds the metadata handed to the app's handler: [1](#0-0) 

The HMAC check is: [2](#0-1) 

`validate_signature` computes the HMAC only over `verifiable_query.to_signable_string`. For webhooks, that method returns solely the raw body, excluding every header: [3](#0-2) 

But the `shop` value passed into `WebhookMetadata` — the value the app is told to trust as "the shop domain of the webhook" — comes straight from the `x-shopify-shop-domain` header, which is never part of the signed content: [4](#0-3) 

The gem's own documentation states `Registry.process` "will verify the request did indeed come from Shopify" and describes `data.shop` as an attribute of the (verified) webhook: [5](#0-4) [6](#0-5) 

**Broken equality:** `shop bound by HMAC` ≠ `shop delivered to handler`. Shopify signs webhook bodies with the single app-level `client_secret` shared across *every* shop that has installed the app — it is not shop-specific. Consequently, any shop that has legitimately installed the app (an ordinary, unprivileged tenant, not a privileged account) can:
1. Receive one legitimate webhook for its own store, capturing a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret.
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, substituting the `x-shopify-shop-domain` header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still succeeds, because it never inspected the shop header — only the byte-identical body.
4. `Registry.process` dispatches to the app's handler with `WebhookMetadata#shop` set to the victim's domain, while the (attacker-controlled) body content is processed as if it legitimately originated from and pertains to the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: an unprivileged tenant can make the host application believe an arbitrary attacker-supplied webhook body pertains to a different, victim tenant, since the library presents `shop` as verified but never actually binds it to the HMAC. Any host app following the documented contract (using `data.shop` to route/act on the correct tenant's records, e.g., updating tenant state, disabling a shop, or processing order/customer data keyed by `data.shop`) is exposed to cross-tenant state corruption purely through this gem's own verification/dispatch guarantee failing to hold.

### Likelihood Explanation
No credentials, access tokens, or privileged access to the app are required — only that the attacker's own shop has installed the app and can receive at least one webhook of any topic (a completely ordinary, unprivileged merchant action), plus the ability to send an HTTP request to the app's public webhook endpoint with a modified header. This satisfies the "unprivileged internet user breaking an identity binding" bar directly.

### Recommendation
Bind the shop identity into the value that is actually HMAC-verified rather than trusting an unauthenticated header:
- Include the shop domain (and/or topic, webhook id) in the canonical string verified by `Utils::HmacValidator`, or
- Independently verify the header-derived `shop` against a value obtained only from verified content (e.g., a per-shop webhook secret, or cross-checking against the app's own registered shop list before dispatch), and
- Update `docs/usage/webhooks.md` to explicitly state that `data.shop` is not covered by HMAC verification if the binding is not fixed, so host apps do not treat it as authenticated.

### Proof of Concept
1. Shop A installs the app and legitimately triggers a webhook (e.g., `orders/create`). The app receives:
   - body: `{"id":1,...}`
   - headers: `x-shopify-hmac-sha256: <valid HMAC of body under shared api_secret_key>`, `x-shopify-shop-domain: shop-a.myshopify.com`
2. Shop A's operator captures this exact `(raw_body, hmac)` pair.
3. Shop A's operator sends a POST to the app's webhook endpoint with the same `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: shop-victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` at [7](#0-6) , which passes because the signature only ever covered the identical `raw_body`.
5. `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "shop-victim.myshopify.com", body: <attacker-influenced body>, ...)` at [8](#0-7) , causing the host app to act on shop-victim's tenant record using attacker-supplied content, despite the webhook never having been signed for, or originated from, that shop.

### Citations

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

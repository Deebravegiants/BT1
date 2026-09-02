### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator.validate` authenticates the body bytes but never the `shop-domain` header. `Registry.process` nonetheless trusts the unauthenticated `shop-domain` header and forwards it as the tenant identifier (`WebhookMetadata#shop`) to the host application's handler. This breaks the identity binding `HMAC-authenticated sender == shop the payload is attributed to`, mirroring the reported bug class where a field acted upon (vested amount/fees) was not actually covered by the accounting/HMAC boundary meant to protect it.

### Finding Description
The webhook HMAC is computed exclusively over the raw body: [1](#0-0) 

`shop`, however, is read straight from an HTTP header, entirely independent of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately hands the (unauthenticated) `request.shop` value to the handler as the source-of-truth tenant identifier: [3](#0-2) 

`HmacValidator.validate` confirms this — it only ever signs/verifies `verifiable_query.to_signable_string`, which for webhooks is just `@raw_body`: [4](#0-3) 

Because a single app has one `client_secret` shared across every merchant that installs it, any merchant who installs the app (an "unprivileged" party with respect to any other tenant) can legitimately trigger a real webhook on their own store and capture a valid `(raw_body, hmac)` pair. That attacker can then replay the exact same body/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` still succeeds — it never inspected the header — so `Registry.process` accepts the request and calls the handler with `shop: <victim-shop>`, even though the payload actually originated from the attacker's own shop.

### Impact Explanation
Downstream `WebhookHandler` implementations are documented to key their logic off `data.shop` (see `docs/usage/webhooks.md` and the `WebhookMetadata` shape exposed by this gem). Since the gem presents `shop` as verified/trusted alongside a passing HMAC check, any host app that (reasonably) treats a validated webhook's `shop` as authoritative can have attacker-controlled body content attributed to, and processed under, a victim tenant — i.e., cross-tenant data corruption/confusion using only a legitimately-owned shop as the attack vector. This matches the Critical "cross-tenant access" impact category: no access token, secret, or privileged account for the *victim* is required, only a standard install of the app on the attacker's own shop.

### Likelihood Explanation
Any merchant can install a public/embeddable app for free and trigger webhooks on their own store (e.g., `orders/create`, `app/uninstalled`) to harvest a valid `(body, hmac)` pair, then POST it to the app's public webhook URL with a forged `shop-domain` header. No secret material is required. This is a mechanical, repeatable, low-effort attack once the app's webhook endpoint URL is known (typically discoverable/guessable, e.g., `/webhooks`).

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated, or otherwise verify the header-provided `shop` against an independent trust source before trusting it as a tenant key — e.g., cross-check `request.shop` against the shop associated with a previously stored, legitimate session for that shop, or require the host app to reject/flag `shop` values it doesn't already have an offline session for. At minimum, the gem's webhook documentation and `WebhookMetadata` API should explicitly state that `shop` is unauthenticated header data and must not be trusted as a tenant boundary without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Attacker performs an action that triggers a subscribed webhook (e.g., `orders/create`), capturing the exact raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent to the app's webhook endpoint.
3. Attacker resends that identical body and HMAC header to the same webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over the (unchanged) body and it matches, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker's crafted body content — despite the request never having come from Shopify on behalf of `victim-shop`.

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

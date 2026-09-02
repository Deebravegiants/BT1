### Title
Webhook `shop`/`topic` fields are unauthenticated relative to the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates its HMAC over the raw HTTP body only, but the `shop` and `topic` values that are trusted and dispatched to the app's handler come from unauthenticated HTTP headers that are never included in the signed material. This breaks the identity binding `shop verified by HMAC == shop acted upon by handler`, the same class of flaw described in the source report: a field that is *acted on* (there, vester token balance for `signalTransfer`; here, the `shop` used for tenant dispatch) is not covered by the mechanism that is supposed to bind identity (there, GMX's token-balance gate; here, the HMAC signature).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from the `shopify-shop-domain` / `shopify-topic` headers, which are not part of the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately dispatches using `request.shop` and `request.topic` taken from the (unverified) headers: [3](#0-2) 

`HmacValidator.validate` recomputes the HMAC purely from `verifiable_query.to_signable_string` (the raw body) and the app's `api_secret_key`, which is shared across every shop that has installed the app: [4](#0-3) 

Because the secret is shared per-app (not per-shop) and the signature covers only the body, any `(raw_body, hmac)` pair that is valid for *one* installed shop (e.g. one the attacker controls, having installed the same app on their own store and captured a genuine webhook delivery) remains a *valid* signature no matter what `shop-domain` / `topic` headers are attached to the replayed request. An unprivileged attacker can:
1. Install the target app on their own shop, capture a legitimate webhook `(body, X-Shopify-Hmac-SHA256)` pair delivered to the app's public webhook endpoint.
2. Replay that exact body+HMAC to the same endpoint, but with the `X-Shopify-Shop-Domain` header rewritten to the victim shop.
3. `HmacValidator.validate` still succeeds (only the body is checked), so `Registry.process` calls the topic handler with `shop: request.shop` pointing at the victim tenant, even though nothing about the victim shop was ever cryptographically confirmed.

This is exactly the binding-equality violation called out in the rules: *"a shop authenticated [by HMAC] versus the shop [acted upon / stored] as a session key"* — here the shop used to key handler logic is not the shop the HMAC actually authenticates.

### Impact Explanation
This allows cross-tenant confusion: an attacker-controlled webhook payload can be attributed to an arbitrary victim `shop` domain inside the app's webhook handler, without holding any credentials for the victim shop. Depending on what the consuming application does with `WebhookMetadata#shop` (e.g., look up/modify per-shop records, trigger per-shop side effects), this can lead to cross-tenant data corruption or state changes attributed to the wrong merchant, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Requires only: (a) the attacker can install the same app on a shop they control to obtain one genuine `(body, hmac)` pair, and (b) the app's webhook endpoint is reachable and does not itself re-derive `shop` from a source that is bound to the HMAC. No `api_secret_key`, access token, or other privileged credential is required — only ordinary unauthenticated HTTP access to the public webhook URL, consistent with the "unprivileged internet user" scope of this analysis.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the material that is actually verified — either require the body to be parsed and cross-checked against an authenticated `shop` claim, or document/enforce that consumers must independently validate `request.shop` against a shop known to have this app installed (e.g., checking it against stored session/shop records) before trusting it, rather than accepting the header value as authenticated solely because `HmacValidator.validate` passed.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) to receive a genuine `(raw_body, X-Shopify-Hmac-SHA256)` pair from Shopify.
2. Attacker sends a POST to the app's public webhook endpoint with the captured `raw_body` and `X-Shopify-Hmac-SHA256` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [5](#0-4)  — validation succeeds because the body/secret pair is genuinely valid.
4. `handler.handle` is invoked with `shop: request.shop` == `"victim-shop.myshopify.com"` [6](#0-5) , letting the attacker's payload be processed as if it originated from the victim tenant.

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

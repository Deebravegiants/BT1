## Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs (and verifies) only the raw request body via HMAC, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` to route and attribute the webhook are taken from HTTP headers that fall entirely outside the signed content. By contrast, the OAuth `AuthQuery` class binds `shop` into `to_signable_string`, so this is an inconsistent, weaker binding specific to the webhook path.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body only for webhooks) and compares it to the `hmac` header via `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` then trusts `request.shop` (an unsigned header) to attribute the webhook to a tenant and dispatches it to the handler: [4](#0-3) 

In contrast, for OAuth callbacks `Auth::Oauth::AuthQuery#to_signable_string` explicitly includes `shop` in the signed content, correctly binding the shop identity to the signature: [5](#0-4) 

The broken equality is: `hmac_valid(body) == hmac_valid(body, shop)`. The gem treats "HMAC of body is valid" as proof that "(body, shop) came from Shopify for that shop," but the `shop` header is never part of what's authenticated.

### Impact Explanation
Because the api_secret_key is shared across all shops that install a given app (it is not per-shop), any attacker who can install/uninstall the app on their own shop (an ordinary, unprivileged merchant action) can obtain a genuinely Shopify-signed `(raw_body, hmac)` pair for a webhook triggered on their own store. Since the HMAC covers only `raw_body`, the attacker can replay that exact body+hmac while substituting the `shopify-shop-domain` (and `shopify-topic`/`webhook-id`) header with an arbitrary victim shop domain. `Registry.process` will pass HMAC validation (body unchanged) and hand `WebhookMetadata` with the attacker-forged `shop` to the app's handler, causing state changes attributed to a shop the attacker does not control — a cross-tenant data/identity confusion via the app's own webhook processing pipeline.

### Likelihood Explanation
Exploitation requires only that the attacker be an unprivileged Shopify merchant able to install the app on their own store and trigger a webhook (e.g. `orders/create`), then replay the captured request body with a modified `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or privileged accounts is required, matching the "unprivileged internet user" threat model.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) as part of the HMAC-signed material in `Webhooks::Request#to_signable_string`, or otherwise cross-check the `shopify-shop-domain` header against an authenticated value (e.g. compare it against a value looked up via the registered session/webhook subscription rather than trusting the header) before dispatching to `handler.handle` in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a genuine webhook POST (e.g. `orders/create`) including its `x-shopify-hmac-sha256` header and raw body.
2. Replay the identical raw body and `hmac-sha256` header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `raw_body` against the secret.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) invokes the app's handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled webhook data as if it originated from the victim's store.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

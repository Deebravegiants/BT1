### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but `to_signable_string` (which is what `Utils::HmacValidator` verifies) only returns the raw body. The HMAC never binds the `shop` claim to the signature, so the tenant identity delivered to the app's webhook handler is unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," and the `shop` field in the resulting `WebhookMetadata` is documented as "The shop domain of the webhook" — i.e. a trusted value: [1](#0-0) [2](#0-1) 

The verification path is: [3](#0-2) 

`Utils::HmacValidator.validate` only checks the HMAC against `verifiable_query.to_signable_string`: [4](#0-3) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body (`@raw_body`), while `shop` is read straight from the header, with no involvement in the signed bytes: [5](#0-4) 

The identity binding that should hold is: `hmac-signed bytes == bytes that determine the tenant (shop) acted upon`. Instead, `hmac-signed bytes == @raw_body only`, while `shop (acted upon, passed to the handler) == unauthenticated header value`. Because the header is never covered by the signature, any request whose body+HMAC pair is valid for the app's secret (e.g., a genuine webhook the attacker's own shop legitimately received from Shopify, replayed directly to the app's webhook endpoint) can have its `x-shopify-shop-domain` header rewritten to name an arbitrary victim shop. `HmacValidator.validate` still returns `true` because it never inspects the shop header, and `Registry.process` forwards `WebhookMetadata.new(... shop: request.shop ...)` with the attacker-chosen shop value to the app's handler: [6](#0-5) 

Any app handler that trusts `data.shop` to scope which merchant's records to update/sync (as the documented example does) will act on the wrong tenant's data using an attacker-controlled shop value that was never authenticated.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an attacker who can obtain any single valid (body, HMAC) pair for the shared app secret — e.g., from their own legitimately installed shop's webhook traffic — can relabel it to any other shop domain and have it processed as if it originated from that victim shop. Downstream handlers that key persistence/sync operations off `data.shop` (as the gem's own documentation recommends) can be made to write, delete, or process the attacker's payload under a victim tenant's identity. This is a cross-tenant access issue.

### Likelihood Explanation
Exploitation requires no secrets beyond having received/observed one legitimate webhook delivery (with its valid HMAC) for any shop using the app — a bar any unprivileged installer of the app on their own store can clear — plus the ability to POST directly to the app's public webhook endpoint with modified headers, which is standard and expected per the documented `process` usage. No `api_secret_key`, access token, or elevated privilege is required.

### Recommendation
Bind the shop identity to the verified payload instead of trusting the header in isolation:
- Extend `VerifiableQuery`/`to_signable_string` for `Webhooks::Request` (or add a parallel check) so the shop domain is cryptographically tied to the request the same way `AuthQuery#to_signable_string` includes `shop` in its signed string (`lib/shopify_api/auth/oauth/auth_query.rb`), or
- Require callers to supply/verify the expected shop out-of-band (e.g., match against the shop the webhook was registered for), and document that `data.shop` must not be trusted as authenticated unless bound to the signature.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker resends `POST /webhook-path` directly to the app with body `B`, `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so validation passes (`lib/shopify_api/utils/hmac_validator.rb:27-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: B, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), and the handler processes the attacker's payload under the victim shop's identity.

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

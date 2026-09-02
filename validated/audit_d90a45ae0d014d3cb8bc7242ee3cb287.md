### Title
Webhook `shop`/`topic` identity is not covered by the HMAC that `Registry.process` verifies, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating an HMAC computed only over the raw request body, then dispatches the request to the app's handler using the `shop` and `topic` values taken from unauthenticated HTTP headers. Because the app's `api_secret_key` is shared across every merchant/tenant that installs the app (it is not per-shop), any tenant that legitimately receives one authentic webhook (body + valid HMAC) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header for a different, victim tenant. The request still passes `HmacValidator.validate`, and the handler is invoked believing the payload belongs to the victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it with the value supplied in the request: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body; `shop`, `topic`, and `webhook_id` are pulled directly from HTTP headers and are never included in the signed material: [2](#0-1) 

`Registry.process` validates the HMAC (i.e., proves the *body* was produced by someone holding `api_secret_key`) and then immediately trusts the header-derived `request.shop` and `request.topic` to construct `WebhookMetadata` that is handed to the app's handler as the tenant identity: [3](#0-2) 

The identity binding that should hold is:
`shop authenticated by the HMAC == shop the handler acts on`

but the implementation actually enforces only:
`body authenticated by the HMAC == body the handler acts on`

while `shop` (and `topic`) are taken from headers with no cryptographic tie to the signature. Since `api_secret_key` (used in `HmacValidator.validate`, see `Context.api_secret_key` usage in `lib/shopify_api/auth/oauth.rb:76`) is the same value for every shop that installs the app, a legitimate, unprivileged tenant can obtain a validly-signed body/HMAC pair from their own store's webhook traffic and reuse it against the app with a forged `shop-domain` header pointing at another tenant.

### Impact Explanation
This is a cross-tenant data-confusion vulnerability: the app processes attacker-supplied (replayed) webhook content while believing it belongs to a different merchant's shop. Depending on how the app's handler uses `WebhookMetadata#shop` (e.g., keying per-tenant records, triggering per-tenant side effects, updating tenant-scoped data), an attacker who is merely one of the app's ordinary merchants can inject data attributed to a victim tenant — a cross-tenant access impact, without needing any of the app's own credentials, the victim's access token, or `client_secret`.

### Likelihood Explanation
Exploitation requires only:
1. Being an ordinary, unprivileged installer of the target app (no special privilege, no leaked secret).
2. Capturing one legitimate webhook body + `x-shopify-hmac-sha256` header sent to your own webhook endpoint (trivial, since you receive your own webhooks).
3. Replaying that exact body/HMAC to the app's public webhook URL with the `shop-domain` (and optionally `topic`) header changed to the victim's shop.

No secrets, tokens, or privileged access are required, and the webhook endpoint is public by design, making this readily reachable by any unprivileged internet user who has installed the app once.

### Recommendation
Bind `shop` (and `topic`) into the material that is cryptographically verified, or otherwise cross-check the header-supplied `shop`/`topic` against a value derived from data that is authenticated per-tenant (e.g., validate that the shop domain is one the app has an active session/installation for, and/or incorporate shop/topic into the signed payload check) before constructing `WebhookMetadata` and invoking the handler in `Registry.process`.

### Proof of Concept
1. Install the target app on shop A (attacker-controlled) and capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` using the app's shared `api_secret_key`).
2. Send a POST directly to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid since only the body is signed)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic: <same or different topic>`
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `B`/`H` are still a valid pair — see [4](#0-3) .
4. The handler is invoked with `WebhookMetadata` whose `shop` is `"victim-shop.myshopify.com"`, even though the data in `B` actually originated from shop A, demonstrating the cross-tenant identity confusion.

### Citations

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

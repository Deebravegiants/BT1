I found a valid analog in the webhook signature verification path.### Title
Webhook `topic` and `shop-domain` headers are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the signed payload [2](#0-1) . `HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against the received `hmac`, i.e. only the body bytes [3](#0-2) . `Registry.process` accepts the request once that check passes and then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values [4](#0-3) .

### Finding Description
This is the same bug class as the report: a field that is acted on (`shop`, used as the tenant identifier for the dispatched `WebhookMetadata`) is not covered by the integrity check (the HMAC) that is supposed to authenticate the whole message. The binding that should hold is:

`hmac == HMAC(secret, body ‖ shop ‖ topic)` (bytes actually verified must equal bytes actually acted upon)

but the implementation only enforces:

`hmac == HMAC(secret, body)` [1](#0-0) [5](#0-4) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that has installed a multi-tenant app, any merchant that installs the app can, on their own store, generate a legitimate webhook delivery (valid `body` + valid HMAC computed by Shopify with the app's shared secret). That merchant can then replay the exact same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a victim shop. `Request#shop`/`Request#topic` simply read these headers [6](#0-5) , and `HmacValidator.validate` still succeeds because it never inspects them [3](#0-2) . `Registry.process` then invokes the registered handler believing the event legitimately belongs to the victim shop/topic [4](#0-3) .

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged internet user who merely controls one tenant of a multi-tenant app can forge webhook events that the gem accepts as originating from an arbitrary other shop, or as an arbitrary other topic (including sensitive/mandatory topics such as `customers/data_request`, `customers/redact`, `shop/redact`) [7](#0-6) . Any downstream logic in the host app's `WebhookHandler` that trusts `WebhookMetadata#shop`/`#topic` to select per-tenant data, credentials, or session records will act on the wrong tenant's behalf, satisfying the "cross-tenant access" impact bar.

### Likelihood Explanation
Requires only that the attacker control one legitimate installation of the target multi-tenant app (a normal, unprivileged merchant relationship, not leaked credentials or `api_secret_key` knowledge) and be able to send an HTTP request to the app's public webhook endpoint with modified headers - no TLS interception, no social engineering, no privileged account needed.

### Recommendation
Include `shop`, `topic` (and any other header field the handler relies on for tenant/topic identity) inside the HMAC-signable string, or otherwise cryptographically bind them to the verified payload, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`/`host`/`state` into its HMAC computation [8](#0-7) . At minimum, `Registry.process` should re-derive `shop`/`topic` only from data that was part of the HMAC-verified bytes, not from independently-supplied headers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker.myshopify.com`) and configures a webhook subscription so Shopify delivers a real webhook to a URL the attacker controls (e.g. a request-capturing endpoint), or simply captures the request as it arrives at the app's actual webhook route.
2. Attacker records the raw request body and the valid `X-Shopify-Hmac-Sha256` header - both were computed and signed by Shopify using the app's shared `api_secret_key`.
3. Attacker re-sends this exact `raw_body` + `hmac` to the app's webhook endpoint but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and optionally `X-Shopify-Topic` to a sensitive topic like `customers/data_request`).
4. `Request#shop`/`#topic` return the attacker-controlled header values [6](#0-5) ; `HmacValidator.validate` still passes because it only checks `body` [3](#0-2) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: "customers/data_request", shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)` [9](#0-8) , causing the host application to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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

This confirms the finding. `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers without being part of the signed payload [2](#0-1) . `Registry.process` validates only this body-only HMAC and then dispatches the handler using the unauthenticated `shop` header value [3](#0-2) . Since Shopify apps use a single app-wide `client_secret` (not a per-shop secret) to sign every merchant's webhooks, this is a genuine cross-tenant identity-binding break.

### Title
Webhook HMAC covers only the raw body, not the `shop-domain`/`topic`/`webhook_id` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only [1](#0-0) , while the `shop`, `topic`, and `webhook_id` values that `Registry.process` trusts and forwards to app handlers come from HTTP headers that are excluded from the signature [2](#0-1) . Because a single app's `client_secret` is used to sign webhooks for every merchant that installs the app, any merchant (an unprivileged internet user who can freely install the app on their own store) can capture a validly-signed webhook body/HMAC pair from their own shop, then replay it with the `shop-domain` (and/or `topic`/`webhook_id`) header swapped to a victim shop, and the signature will still validate.

### Finding Description
`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` to build the string that gets HMAC'd against `Context.api_secret_key` [4](#0-3) . For webhook requests, `to_signable_string` is simply the raw body [1](#0-0) ; the `shop`, `topic`, and `webhook_id` accessors read straight from (attacker-controllable) headers with no cryptographic binding to that signature [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [3](#0-2) .

The identity binding that should hold is: `shop header == shop cryptographically bound by the HMAC`. In this implementation that equality never holds — the HMAC binds only the body bytes, not the tenant identity attached to them. Since `client_secret` is one value per app (shared across every merchant/tenant that installs it, as reflected by `Context.api_secret_key` being a single global value used for all shops [5](#0-4) ), any merchant who legitimately receives real, validly-signed webhooks for their own store can reuse that signature with a different `shop-domain` header and have it accepted as if it came from a different tenant.

### Impact Explanation
This breaks the tenant boundary that host applications rely on: they trust `WebhookMetadata#shop` (sourced from `request.shop`) to decide which merchant's records to update/read/delete in response to the webhook payload, because `Registry.process` already asserted "this request passed Shopify's HMAC check." An attacker who is a legitimate merchant of the app (a normal internet user who installs the app for free/trial on their own store) can:
1. Trigger any webhook topic on their own shop to get a real `(raw_body, hmac)` pair signed with the shared `client_secret`.
2. Replay that exact body+HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) with a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it never inspects those headers, and the host app's handler processes attacker-chosen body content under the identity of the victim shop.

This is a cross-tenant access vector: an unprivileged (merchant-level, not privileged) attacker can inject data or trigger actions attributed to another tenant without ever needing the victim's or the app's actual credentials, satisfying the "cross-tenant access" Critical impact bar.

### Likelihood Explanation
Likelihood is significant for any app built on this gem that installs on multiple independent shops (the standard SaaS model) and processes webhook bodies without doing additional out-of-band shop verification. Obtaining a legitimate signed webhook is trivial (install the app, trigger any event on your own store), and no secret material beyond normal self-service app installation is required.

### Recommendation
Bind the tenant/topic identity into the signed material, e.g. verify the HMAC over a canonical string that includes `shop`, `topic`, and `webhook_id` in addition to the raw body (mirroring how `AuthQuery#to_signable_string` binds `shop`/`state`/etc. into its signature at `lib/shopify_api/auth/oauth/auth_query.rb`), or otherwise reject/flag webhook requests whose header-derived `shop` cannot be independently corroborated (e.g., cross-check against the app's known installed-shop list) before dispatching to handlers.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker-shop.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: headers (`x-shopify-topic`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-webhook-id`) and raw JSON body.
2. Resend the identical raw body and `x-shopify-hmac-sha256` value to the same webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and, if desired, a different `x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates successfully because `to_signable_string` only hashes `@raw_body` [1](#0-0) .
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, even though this data never actually originated from Shopify for that shop [3](#0-2) .

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** lib/shopify_api/context.rb (L78-90)
```ruby
        @api_key = api_key
        @api_secret_key = api_secret_key
        @api_version = api_version
        @api_host = api_host
        @host = T.let(host, T.nilable(String))
        @is_private = is_private
        @scope = Auth::AuthScopes.new(scope)
        @is_embedded = is_embedded
        @logger = logger
        @private_shop = private_shop
        @user_agent_prefix = user_agent_prefix
        @old_api_secret_key = old_api_secret_key
        @response_as_struct = response_as_struct
```

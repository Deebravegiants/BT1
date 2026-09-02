### Title
Webhook shop-domain identity is unauthenticated / not bound to the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` uses the HMAC covering only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers that are never included in the signed data. `Registry.process` accepts the request as authentic for the shop named in the header as soon as the body's HMAC checks out, without any binding between the signature and the shop identity claimed in the header.

### Finding Description
`HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-31`) verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`. For webhook requests, `to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`). None of `shop`, `topic`, or `webhook_id` participate in the signed string — they are pulled straight from attacker-controllable HTTP headers via `shopify_header` (`lib/shopify_api/webhooks/request.rb:15-33`, `67-70`).

`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) only checks `Utils::HmacValidator.validate(request)` (i.e., body signature) and then dispatches the handler using the *unauthenticated* `request.shop`/`request.topic`:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
The identity binding the code implicitly assumes is: `hmac_valid(raw_body) == request_is_authentically_from(request.shop)`. That equality does not hold, because `raw_body` alone does not encode `shop`. Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` — trivially available to any merchant who installs the app on their own store and receives a legitimate webhook — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. Since the secret is shared across all shops using the app (it is the app's `client_secret`, not a shop-specific secret), the signature still validates, but `request.shop` now points to any shop the attacker chooses, including a shop they do not control.

### Impact Explanation
This breaks the shop-identity binding at the trust boundary of webhook processing. If the host application (using the gem as documented) keys any tenant-affecting action off `WebhookMetadata#shop` — e.g., deprovisioning on `app/uninstalled`, GDPR data deletion on `shop/redact`, or other lifecycle actions — an attacker can forge these events for a victim shop they never installed the app on, achieving cross-tenant action forgery using only a webhook body/HMAC pair they legitimately received for their own shop (many webhook topics, such as `app/uninstalled`, have static or near-empty bodies, making this trivial). This satisfies the "cross-tenant access" criterion, since a real webhook boundary intended per-shop is defeated for shops sharing the same app credential.

### Likelihood Explanation
Any user who can install the app on any store (an ordinary, unprivileged action) can capture a valid `(body, hmac)` pair for topics with predictable/empty bodies and replay it against the webhook endpoint with a spoofed `shop-domain` header. This requires no access to `api_secret_key`, tokens, or TLS interception — only sending an HTTP POST to the app's public webhook endpoint, which is the normal way this gem is invoked (`Registry.process(request)`).

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified for webhook requests, or otherwise cryptographically bind the header-derived shop to the signature (e.g., verify the shop header against a shop the app has an active, previously-established session/installation record for, and/or require the HMAC to cover a canonical string containing shop+topic+body, not just the raw body). At minimum, document and enforce that consumers must independently corroborate `request.shop` against a known-installed shop before trusting `WebhookMetadata#shop` for privileged actions.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook with a static/empty body, e.g., `app/uninstalled` with body `{}`.
2. Capture the raw body and the `X-Shopify-Hmac-Sha256` header Shopify sent (valid because it's HMAC-SHA256 of `{}` with the shared `client_secret`).
3. Replay a POST to the victim app's webhook endpoint with the same body `{}` and the same HMAC header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` (body/HMAC match) and `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"`, causing the app to perform the uninstall/redact logic for a shop the attacker never controlled. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

## Title
Webhook HMAC only signs the raw body, so `shop`, `topic`, and `webhook_id` used for tenant routing are forgeable - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers to dispatch webhook data to app handlers, while the HMAC signature that is supposed to authenticate the request only covers the raw body. This breaks the identity binding `shop asserted-by-header == shop actually authenticated-by-HMAC`, allowing a replay of a *genuinely signed* body (obtainable by any unprivileged party who can trigger a real webhook for their own shop, since the signing secret is the app-level `client_secret`, not shop-specific) against a spoofed `shopify-shop-domain`/`shopify-topic` header pair to make the host app process attacker-chosen data under a victim shop's tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read straight from HTTP headers and are never part of the signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then uses the *unauthenticated* header-derived `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` only compares the HMAC over `verifiable_query.to_signable_string` (i.e., the body) against the secret — it has no knowledge of `shop`/`topic`/`webhook_id`: [4](#0-3) 

Because the HMAC secret is the app's single `client_secret` (identical across every merchant that installs the app), a valid `(raw_body, hmac)` pair produced for **any** shop's genuine webhook delivery is valid for **any** shop header value. The binding that should hold is:

`shop authenticated by HMAC == shop acted upon by the handler`

but in reality: `shop acted upon by the handler == shop header (unauthenticated)`, while HMAC only authenticates the body. An attacker who installs the same app on their own store (an unprivileged action) can capture a legitimately-signed webhook body/HMAC pair and resend it to the app's public webhook endpoint with the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) headers rewritten to a victim shop, causing the host app to process that data as if it genuinely originated from the victim tenant.

### Impact Explanation
This crosses a tenant boundary: an app that keys any per-shop side effect (e.g., `app/uninstalled` cleanup, order/customer data ingestion, billing state) off `WebhookMetadata#shop` will act on a victim shop's tenant context using attacker-supplied body content and topic, without ever needing the victim's credentials. This matches the "cross-tenant access" Critical-impact category since it lets one merchant force data to be attributed/actioned against a different merchant's tenant scope through the gem's own webhook verification API.

### Likelihood Explanation
Exploitation only requires: (1) being able to install the target app on any shop (commonly self-serve for public apps) to obtain one legitimately HMAC-signed webhook body, and (2) sending a crafted HTTP POST to the app's public webhook endpoint with the captured body/HMAC and a rewritten shop/topic header — no access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind the authenticated identity fields into the HMAC-covered signable string (or otherwise cryptographically bind `shop`, `topic`, and `webhook_id` to the signature), or require that the host app independently verify the resolved `shop` against a shop it has actually installed/authorized (e.g. cross-check against stored session/tenant data) before dispatching to handlers, rather than trusting header-only fields alongside a body-only HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a real webhook delivery with a valid `shopify-hmac-sha256` header computed over some `raw_body` using the app's `client_secret`.
2. Attacker captures `raw_body` and `hmac` from this delivery.
3. Attacker sends a POST to the app's public webhook endpoint with headers:
   - `x-shopify-topic: <topic>` (any registered topic)
   - `x-shopify-hmac-sha256: <captured hmac>`
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-webhook-id: <arbitrary>`
   and body `raw_body` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) validates the HMAC successfully (it only checks the body) and calls the handler with `shop: "victim-shop.myshopify.com"`, causing the host app to act on the victim's tenant context using attacker-controlled webhook data.

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

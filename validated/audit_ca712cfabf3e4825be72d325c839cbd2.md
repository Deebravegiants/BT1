## Title
Webhook `shop` (tenant identifier) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body when validating a webhook's HMAC, while the `shop` (and `topic`/`webhook_id`/`api_version`) values used to route and process the webhook are read directly from unauthenticated HTTP headers. Because the app's `api_secret_key` is a single shared secret across all shops that installed the app (it is not shop-specific), any shop that legitimately receives a genuine, correctly-signed webhook can replay that exact body/HMAC pair while swapping the `X-Shopify-Shop-Domain` header to name a different ("victim") shop. `ShopifyAPI::Webhooks::Registry.process` accepts this forged request as valid and dispatches it to the host application's handler tagged with the attacker-chosen shop, breaking the identity binding `shop_that_is_HMAC-verified == shop_the_handler_acts_on`.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `HmacValidator.validate`, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler — there is no check that the `shop` header matches any shop-scoped expectation: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the signature purely from `verifiable_query.to_signable_string` (the raw body) and the app's single `Context.api_secret_key`, which is identical for every shop that has this app installed: [4](#0-3) 

Because the secret is shared across tenants and the `shop` header is outside the signed material, the equality the gem should enforce — `hmac-authenticated-body's-shop == shop-passed-to-handler` — does not hold. Any attacker who has one legitimate, currently-installed shop can capture a genuine webhook (body + valid HMAC) for a topic such as `app/uninstalled`, `customers/data_request`, or `customers/redact`, and re-POST the identical body/HMAC to the app's webhook endpoint with `X-Shopify-Shop-Domain` changed to a victim shop's domain. The signature still validates (it only covers the body, and the secret is app-wide, not shop-specific), so `Registry.process` calls the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: attacker's body, ...)`.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: an unprivileged holder of one shop's credentials can cause the host application to process arbitrary attacker-controlled webhook payloads *as if* they originated from a different, victim shop. Depending on how the host app's handlers use `WebhookMetadata#shop` (e.g., marking a shop as uninstalled and revoking access, triggering GDPR data-erasure/redaction workflows against the victim's data, or updating per-shop settings/state keyed by `shop`), this can cause cross-tenant data corruption, unauthorized state changes, or disruption of a merchant's app installation — all attributable to `Registry.process` trusting an HMAC-unauthenticated header field as a tenant identifier.

### Likelihood Explanation
Exploitation only requires the attacker to install the app on their own store (to obtain one genuine signed webhook body/HMAC pair for a topic of interest) and to be able to send an HTTP POST to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header — no access token, `client_secret`, or privileged account is needed, matching the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` (and `topic`/`webhook_id`) claim cryptographically to the HMAC-verified material, or otherwise require the host application to cross-check `request.shop` against an out-of-band trusted value (e.g. compare against the shop associated with the session/subscription that a webhook was registered for) before acting on it. At minimum, document prominently that `request.shop` is unauthenticated header data and must not be trusted as a tenant identity without additional verification, and consider including the shop domain in the signable string used for HMAC validation if Shopify's webhook signing ever supports it, or require applications to validate the delivered shop against known/registered shops before dispatch.

### Proof of Concept
```ruby
# Attacker installs the app on their own store "attacker-shop.myshopify.com" and
# receives a genuine webhook, e.g. for topic "customers/redact":
raw_body = '{"customer":{"id":123},"shop_id":999}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker replays the identical body/HMAC, but swaps the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, not signed
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HMAC validation passes because it only checks raw_body against the app-wide secret:
ShopifyAPI::Utils::HmacValidator.validate(forged_request) # => true

# Registry.process dispatches to the handler with shop: "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(forged_request)
# Handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "customers/redact", body: raw_body)
# even though this webhook never originated from Shopify for that shop.
```

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

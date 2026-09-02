### Title
Webhook Shop/Topic Header Spoofing — HMAC Does Not Cover Routing Identity Fields - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by validating the HMAC over the raw request body only, but then trusts the `shop` and `topic` values taken from unsigned HTTP headers to route the payload to a handler and to build the `WebhookMetadata` passed to app code. The HMAC signature never binds these header values, so the identity of "which shop/topic this payload belongs to" is not verified — only the byte content of the body is.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body`. The `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.topic` and `request.shop` to select the registered handler and to construct the metadata handed to the app's business logic: [3](#0-2) 

The equality that should hold is:
`shop_that_the_HMAC_authenticates == shop_the_handler_acts_on`

but in this code the left side is never computed — the HMAC only authenticates the body bytes, while the right side is read from an attacker-controllable header. Because Shopify signs webhooks for all shops installed on an app with the same app-level `api_secret_key` (it is not a per-shop secret), a `(body, hmac)` pair that is valid for one shop's webhook delivery remains a byte-for-byte valid HMAC no matter what `shop-domain`/`topic` header is attached to the request when it is replayed to the app's webhook endpoint. `Utils::HmacValidator.validate` (used by `Registry.process`) only recomputes and compares the digest of the body: [4](#0-3) 

it has no way to detect that the `shop-domain` header was swapped, since that header was never part of the signed material.

### Impact Explanation
An attacker who can obtain one genuine `(body, hmac)` pair for a webhook (e.g., a webhook delivered for their own shop, or one otherwise captured) can resubmit the exact same request to the app's webhook endpoint while altering the `X-Shopify-Shop-Domain` header to name a different, victim shop. `Registry.process` will pass `HmacValidator.validate` (the body/signature match is untouched) and will then dispatch `handler.handle` with `WebhookMetadata` claiming the payload belongs to the victim shop. Any app logic that trusts `WebhookMetadata#shop` to look up or mutate per-tenant state (session storage, data deletion for `shop/redact`/`customers/redact`, order/customer records, etc.) will act on the wrong tenant's data using attacker-supplied body content — a cross-tenant data integrity/confidentiality break rooted in this gem's failure to bind the shop identity to the HMAC it verifies.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(body, hmac)` pair, which in practice means either intercepting a real webhook delivery to the app or triggering deliveries for their own tenant and forwarding them with a modified `shop-domain` header to the target app instance. This does not require the app's `client_secret` or any privileged credential, only network delivery of a crafted HTTP request to the app's public webhook endpoint, so it is reachable by an unprivileged actor with a normal store, making likelihood moderate.

### Recommendation
Include the shop domain and topic (and any other header used for routing/authorization decisions) in the HMAC-signable material, or independently validate `request.shop` against the shop associated with the registered handler/session before acting on the payload, so that a byte-identical replay with a modified header cannot be misattributed to a different tenant.

### Proof of Concept
1. App has `ShopifyAPI::Webhooks::Registry` configured with an `:http` handler for topic `customers/redact` (a mandatory topic acting on tenant data).
2. Attacker installs the app on their own store "attacker.myshopify.com" and triggers a `customers/redact` webhook for their store, or otherwise obtains one valid `(raw_body, X-Shopify-Hmac-Sha256)` pair delivered by Shopify to the app's webhook endpoint.
3. Attacker resends the exact same HTTP request to the app's webhook endpoint, keeping `raw_body` and the `X-Shopify-Hmac-Sha256` header untouched, but replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) succeeds because it only checks the body's HMAC.
5. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))`, causing the app's redaction/handler logic to act against `victim-shop.myshopify.com` using attacker-controlled body content.

### Citations

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

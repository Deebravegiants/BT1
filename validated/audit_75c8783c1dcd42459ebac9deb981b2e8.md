## Title
Webhook shop identity spoofing due to `shop-domain` header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `Webhooks::Registry.process` accepts the request as long as the HMAC over the *body* is valid, then hands the header-derived `shop` value to the application's webhook handler. Because the shop identity is never bound into the signed payload, any request carrying a validly-HMAC'd body can be relabeled to any shop the attacker chooses.

### Finding Description
The identity binding that should hold is:

`shop value the HMAC signature actually authenticates == shop value the handler acts on`

`Utils::HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from HTTP headers, which are not part of the signed material at all: [3](#0-2) 

`Registry.process` validates only the body HMAC, then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the HMAC never covers the headers, `validate_signature`'s `OpenSSL.secure_compare` check passes for **any** combination of headers as long as the raw body and its HMAC pair are unchanged: [5](#0-4) 

An attacker who controls (or briefly trials) any Shopify store that has the target app installed can receive a completely genuine, correctly-signed webhook delivery for their own shop. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and, if desired, `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body, so `Registry.process` dispatches to the handler with `shop: request.shop` set to the victim's domain — a shop that never actually generated this event.

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC check is meant to provide: the value trusted as "the shop this webhook is about" is not the value actually covered by the cryptographic proof. Any host application that keys persistence, authorization, or side effects (e.g., updating orders/inventory/customer records, gating billing state, writing tenant-scoped rows) off `WebhookMetadata#shop` will process attacker-authored event content under a victim tenant's identity — a cross-tenant access/data-confusion primitive, which the rules classify as Critical impact.

### Likelihood Explanation
Any unprivileged internet user who can install/trial the target app on a store they control can obtain a genuinely signed webhook body/HMAC pair for arbitrary event content they trigger themselves (e.g., by editing a product, updating an order, etc., on their own store). No access token, `client_secret`, or privileged account is needed — the attacker only needs a webhook delivery aimed at their own tenant, which they fully control, and the ability to POST an HTTP request with modified headers to the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value that is HMAC-verified (or otherwise cryptographically bind them to the body/signature), or cross-check the header-derived `shop` against a shop already known to the app (e.g., an existing, previously-authorized session/tenant record) before dispatching to the handler. At minimum, `Webhooks::Request#to_signable_string` should not diverge from the set of fields actually trusted downstream in `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a store they control) and subscribes it to a webhook topic (e.g. `orders/create`).
2. Attacker triggers the event on their own store, capturing the real webhook HTTP request Shopify sends, including the `x-shopify-hmac-sha256` header and raw JSON body.
3. Attacker replays this exact request to the app's public webhook endpoint, but changes only the `x-shopify-shop-domain` header value to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` (unchanged) and it matches — validation succeeds.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though the payload originated from the attacker's own store. [6](#0-5) [7](#0-6)

### Citations

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

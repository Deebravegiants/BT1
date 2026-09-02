### Title
Webhook Shop-Domain and Topic Not Bound to HMAC, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then dispatches to a handler and constructs `WebhookMetadata` using the `shop` and `topic` values taken from unauthenticated HTTP headers. Because those identity-bearing fields are never included in the signed material, anyone holding one validly-signed webhook body (any merchant with the app installed legitimately receives such bodies from Shopify) can resend that same body with a forged `shop-domain`/`topic` header pair and have the app process it as if it came from a different tenant or a different event.

### Finding Description
The equality the gem is supposed to enforce is:
`shop/topic asserted to the handler == shop/topic actually covered by the HMAC signature`

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read directly from HTTP headers, independent of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC of the request (i.e., only the body) and then trusts `request.topic` to select the handler and `request.shop` to attribute the event, with no cross-check between the signed body and these header-derived identifiers: [3](#0-2) 

This is unlike `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` (along with `code`, `host`, `state`, `timestamp`) is explicitly included in `to_signable_string` and therefore is bound to the HMAC: [4](#0-3) 

The `HmacValidator.validate` routine only ever verifies whatever `to_signable_string` returns, using the app's `api_secret_key`, which is the same secret shared across every merchant install of the app (it is not shop-specific): [5](#0-4) 

Since the same `api_secret_key` signs webhook bodies for every shop that has the app installed, any merchant who receives a legitimately-signed webhook body for their own store can replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain` and/or `shopify-topic` headers. `Utils::HmacValidator.validate(request)` still succeeds because it only checks the (unmodified) body against the (unchanged) secret, and `Registry.process` then invokes the handler for the attacker-chosen topic and constructs `WebhookMetadata` attributing the body to the attacker-chosen shop: [3](#0-2) 

### Impact Explanation
An app that persists or acts on webhook data keyed by `WebhookMetadata#shop` (e.g., updating per-tenant order/customer records, or triggering `shop/redact`, `customers/redact`, `customers/data_request` mandatory-compliance handlers) can be made to associate one merchant's legitimately-received webhook payload with a different, victim merchant's tenant, or to invoke a handler for a topic the body was never actually generated for. This is a cross-tenant data/handler-confusion issue reachable by any user who has installed the app on their own store — no access token, `client_secret`, or privileged account is required beyond normal app installation.

### Likelihood Explanation
Likelihood is moderate to high: exploitation only requires installing the target app on an attacker-controlled development store (a normal, unprivileged action), capturing one legitimately delivered webhook, and replaying it to the app's public webhook endpoint with modified headers. No secret material needs to be extracted; the HMAC remains valid because it was never computed over the header fields being forged.

### Recommendation
Bind the shop/topic identity to the signed payload before trusting it, e.g. by including `shop`, `topic`, and `webhook_id` in the HMAC-signable string (if Shopify's delivery signing scheme is changed to support this), or — more practically within the current constraint that Shopify only signs the body — have `Registry.process`/`WebhookMetadata` cross-validate that the claimed `shop` is one for which this application currently holds an active session/installation record, and reject/flag webhooks whose `topic` does not match the schema of the parsed body, rather than trusting the headers unconditionally once the body HMAC checks out.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`.
2. Trigger any webhook topic the app is subscribed to (e.g. `orders/create`) to receive a legitimate `POST` from Shopify with headers `x-shopify-hmac-sha256`, `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker.myshopify.com`, and some raw JSON body `B`.
3. Replay the exact same body `B` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and optionally change `x-shopify-topic` to another registered topic such as `customers/data_request`).
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against the app's shared `api_secret_key`: [6](#0-5) 
5. `Registry.process` dispatches to the handler registered for the forged topic and passes `shop: "victim.myshopify.com"` in `WebhookMetadata`, causing the app to act on `victim.myshopify.com`'s tenant data using attacker-supplied body content: [7](#0-6)

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

### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw body, then hands the handler a `shop` value taken from an HTTP header that is never covered by that signature. Since the app's `client_secret` (the HMAC key) is the same for every shop that installs the app, any merchant who has installed the app can obtain a validly-signed webhook body from their own store and replay it to the app's webhook endpoint with a forged `shop-domain` header naming a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read straight from HTTP headers that are excluded from the signed payload: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies exactly and only `verifiable_query.to_signable_string` against `verifiable_query.hmac`: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` treats a passing HMAC check as proof of authenticity for the whole request, then forwards `request.shop` (the unauthenticated header) to the app's handler as the tenant identity: [4](#0-3) 

The broken binding is:
`shop_value_delivered_to_handler (request.shop, from header)` ≠ `shop_whose_event_actually_produced_the_HMAC-signed_body`

The HMAC only proves "signed with this app's `client_secret`" — it says nothing about which of the app's installed shops produced the body, because `client_secret` is shared across every install of the same app. A merchant who has legitimately installed the app can trigger an event in their own store (e.g. `orders/create`), capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair — both of which are cryptographically valid for that app's secret — and resend the exact same body/HMAC pair to the app's webhook endpoint while substituting `x-shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` will accept it, and `Registry.process` will invoke the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though that shop had nothing to do with the event.

Any app whose webhook handler keys its persistence, authorization, or side effects (e.g. "look up the merchant record for `data.shop` and mutate it") off `WebhookMetadata#shop` without independently confirming that shop actually has this webhook registered/installed will process attacker-controlled data under a victim tenant's identity.

### Impact Explanation
This is a cross-tenant data integrity/access issue: an attacker who is merely a regular installer of the app (no special credentials, no access token, no `client_secret`) can cause the app to attribute forged webhook payloads to an arbitrary other shop's tenant context, because the shop identity used by `Registry.process`/`WebhookMetadata` is never bound into the HMAC.

### Likelihood Explanation
Any threat actor can install a public/embedded app on their own development or trial store for free, generate a real event to capture a validly-signed body+HMAC pair, and replay it with a different `x-shopify-shop-domain` header value. No secrets, tokens, or privileged access are required beyond normal app installation.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or independently verify `request.shop` against a source of truth before trusting it:
- Include the `shop-domain` header (and other identity-bearing headers) in `to_signable_string`, changing the signature computation to cover header+body, OR
- After HMAC validation, cross-check `request.shop` against the set of shops that have this app installed / this webhook registered (e.g., via stored `Auth::Session`) before acting on `WebhookMetadata#shop`, rather than trusting the header value implicitly.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a genuine webhook for `orders/create`, capturing:
   - `raw_body` = `{"id":1,...}`
   - `x-shopify-hmac-sha256` = `<valid HMAC over raw_body using the app's shared client_secret>`
2. Attacker POSTs to the app's webhook endpoint reusing the same `raw_body` and `x-shopify-hmac-sha256`, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate` succeeds (it only checks `raw_body` against the HMAC), and `Registry.process` invokes the app's `orders/create` handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`.
4. Any handler logic that looks up/updates state keyed by `data.shop` now operates on the victim tenant using attacker-supplied body content.

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

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. Because the HMAC secret (`Context.api_secret_key`) is the same for every shop that has the app installed, any unprivileged user who installs the app on their own (attacker-controlled) shop can obtain a validly-signed webhook body/HMAC pair, then replay that exact body+HMAC to the host application's webhook endpoint while substituting an arbitrary victim `x-shopify-shop-domain` header. `Webhooks::Registry.process` accepts this as authentic and dispatches the handler with the attacker-chosen `shop`, breaking the equality that should hold between "the shop whose secret produced this HMAC" and "the shop the handler believes sent this webhook."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop`, `topic`, `webhook_id`, `api_version` are parsed straight from headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it authenticates the body bytes and nothing else: [3](#0-2) 

`Webhooks::Registry.process` relies solely on that HMAC check before dispatching the handler with the (unauthenticated) `request.shop`: [4](#0-3) 

Since `Context.api_secret_key` is the app's single `client_secret`, shared across every merchant that installs the app, an attacker who installs the app on their own shop receives legitimately-HMAC-signed webhooks from Shopify. They can extract the `(raw_body, hmac)` pair from a webhook Shopify sent them (e.g. by controlling a payload field, or simply replaying any webhook body they legitimately received) and POST it to the host application's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` recomputes the HMAC over the body only, finds it valid (same secret, same body), and `Registry.process` calls `handler.handle` with `shop: request.shop` set to the forged victim domain.

Equality that is broken: **shop that produced the HMAC (attacker's own shop) == shop the handler trusts as the event source (arbitrary victim shop)**. The gem verifies the bytes of the body but never binds those bytes — or the resulting trust decision — to the specific shop header value the handler consumes.

### Impact Explanation
This lets an unprivileged internet user (anyone able to install the app on a shop they control, which requires no special privilege) forge webhook events that the host application will process as if they originated from any other merchant shop of the attacker's choosing. Depending on how the host app's webhook handlers use `data.shop` (e.g., `app/uninstalled`, `orders/create`, `app_subscriptions/update`), this can lead to cross-tenant state corruption, false uninstall/billing events being recorded against a victim shop, or triggering business logic keyed off shop identity for a shop the attacker does not control. Per the Critical impact category, this is a cross-tenant access vulnerability.

### Likelihood Explanation
Likelihood is high: the only prerequisite is installing the app on an attacker-controlled development/trial shop (a routine, unprivileged action for any public or custom Shopify app), and crafting an HTTP POST with a modified header. No access token, `api_secret_key`, or victim credentials are required — the attacker only needs one legitimately-signed body/HMAC pair from their own installation.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material that `HmacValidator` verifies, or independently verify that the `shop-domain` header matches a shop actually known to have triggered this specific signed payload (e.g., cross-check against the webhook subscription/shop registered for that topic) before dispatching to handlers, rather than trusting the raw header value once the body-only HMAC passes.

### Proof of Concept
Using the same setup pattern as `test/webhooks/registry_test.rb`:

```ruby
body = "{\"order_id\":123}"
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

# Attacker legitimately receives this (body, hmac) pair from their own shop's webhook delivery.
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => Base64.encode64(hmac),
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # attacker substitutes victim's domain
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

# Passes HMAC validation because the signature only covers `body`, not the shop header.
ShopifyAPI::Webhooks::Registry.process(forged_request)
# => handler.handle is invoked with data.shop == "victim-shop.myshopify.com"
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

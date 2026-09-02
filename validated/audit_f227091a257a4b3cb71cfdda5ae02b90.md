### Title
`Registry.process` trusts the attacker-supplied `X-Shopify-Shop-Domain` header without binding it to the HMAC-signed content or to the registration that owns the handler, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`Utils::HmacValidator.validate` only signs/verifies `Request#to_signable_string`, which is the raw body [1](#0-0) , while `Request#shop` is read from the unsigned `shop-domain` header [2](#0-1) . `Registry.process` validates the HMAC, looks up the handler purely by `request.topic` (a single global entry per topic, not per shop) [3](#0-2) , and then hands the handler a `WebhookMetadata.shop` built straight from the unauthenticated header, with no comparison against the shop the registration/session belongs to.

### Finding Description
Binding claimed to hold: `registration.session.shop == request.shop`. Tracing the code shows this binding is never checked and, worse, `Registration` (`lib/shopify_api/webhooks/registration.rb`) has no shop/session field at all — `add_registration` stores one handler per topic globally [4](#0-3) , and `register(topic:, session:)` only uses the session to call Shopify's GraphQL API to create the subscription for that shop; it does not store the session anywhere in the registry [5](#0-4) .

At delivery time, `Registry.process`:
1. Validates HMAC over the raw body only, using `Context.api_secret_key`/`old_api_secret_key` [6](#0-5) .
2. Looks up `@registry[request.topic]` — keyed purely by topic, with no shop dimension [7](#0-6) .
3. Builds `WebhookMetadata` directly from `request.shop`, i.e., the `shop-domain` header, and invokes `handler.handle` [8](#0-7) .

Since the signable string is only the raw body [1](#0-0) , the `shop-domain` header is **not covered by the HMAC**. An attacker who installs the app on their own development shop legitimately receives real, validly-signed webhook callbacks (body + HMAC computed with the real `client_secret`) for their own shop. They can then replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint any number of times while substituting an arbitrary `X-Shopify-Shop-Domain` header value naming a different (victim) shop. `HmacValidator.validate` still passes (it never looks at the shop header), the topic-keyed handler still resolves, and `WebhookMetadata.shop` is set to the attacker-chosen victim shop domain. Any app-side handler logic that uses `data.shop` to select which merchant's records, tokens, or state to update will operate on the attacker's forged shop identity while attacker fully controls the JSON body content (since it's their own webhook payload).

No existing guard in this gem prevents this: `HmacValidator` doesn't touch the shop field, `ShopValidator.sanitize!` is not invoked in this path, there is no `state` comparison, and `Registration`/`Registry` carry no session or shop binding to check against.

### Impact Explanation
This is a cross-tenant data-integrity/confusion issue: the app is told "this signed data came from shop X" when it actually came from an attacker replaying their own shop's data while naming shop X. Depending on how the app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to look up the merchant record, invalidate/update state, or trigger GDPR-style deletion flows), this can let an attacker inject fabricated event data attributed to an arbitrary victim shop domain, repeatable at will against any shop name they choose (they don't even need the victim to exist). This matches the "cross-tenant access" critical category, since one tenant's forged/replayed data is attributed to and acted upon as another tenant's data with no re-validation.

### Likelihood Explanation
Attacker cost is low: only requires installing the target app on their own free/dev shop (fully within the described unprivileged attacker capability) to receive one legitimately signed webhook, then scripting repeated POSTs to the app's public webhook endpoint with a modified `shop-domain` header. No secrets, tokens, or victim cooperation are needed. This is fully repeatable and requires no special app configuration beyond having any HTTP webhook registered — which is the gem's supported/documented mode.

### Recommendation
Bind the accepted shop to context the app already trusts, e.g.:
- Include the `shop-domain` header value in the HMAC-signed content (not currently possible since Shopify itself doesn't sign headers) — since that's a platform limitation, the gem should instead require/encourage the host app to independently authenticate the shop (e.g., cross-check against `Context` shop allowlist or a registered session for that topic+shop) before trusting `WebhookMetadata.shop`, and document clearly that `request.shop` is unauthenticated and must be validated against the app's own shop store, or
- Extend `Registration`/`Registry` to be keyed by `(shop, topic)` when registrations are shop-specific, and have `Registry.process` reject requests whose `request.shop` doesn't correspond to a known, previously-registered shop for that handler.
- At minimum, add explicit documentation/warnings in `WebhookHandler` that `data.shop` is derived from an unauthenticated header and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
```ruby
# test/webhooks/registry_cross_shop_test.rb
require "test_helper"

class RegistryCrossShopTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_same_signed_body_accepted_for_five_different_shop_headers
    handled_shops = []
    handler = Class.new do
      include ShopifyAPI::Webhooks::WebhookHandler
      define_method(:handle) { |data:| handled_shops << data.shop }
    end.new

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http, path: "/webhooks", handler: handler,
    )

    raw_body = '{"id":1}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", "secret", raw_body),
    ).strip

    %w[shop-a.myshopify.com shop-b.myshopify.com shop-c.myshopify.com
       shop-d.myshopify.com shop-e.myshopify.com].each do |shop|
      request = ShopifyAPI::Webhooks::Request.new(
        raw_body: raw_body,
        headers: {
          "X-Shopify-Topic" => "orders/create",
          "X-Shopify-Hmac-Sha256" => hmac,
          "X-Shopify-Shop-Domain" => shop, # attacker-controlled, unsigned
        },
      )
      ShopifyAPI::Webhooks::Registry.process(request) # must NOT raise
    end

    assert_equal 5, handled_shops.uniq.size
    assert_equal %w[shop-a.myshopify.com shop-b.myshopify.com shop-c.myshopify.com
                    shop-d.myshopify.com shop-e.myshopify.com], handled_shops
  end
end
```
Assertion of the broken binding: before processing, `registration` (added via `add_registration`) has no `session`/`shop` attribute at all to compare against `request.shop`; after processing, `handler.handle` is invoked 5 times with 5 distinct `WebhookMetadata.shop` values using the identical `(raw_body, hmac)` pair, proving `Registry.process` never enforces `registration_shop == request.shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L25-45)
```ruby
        def add_registration(topic:, delivery_method:, path:, handler: nil, fields: nil, filter: nil,
          metafield_namespaces: nil)
          @registry[topic] = case delivery_method
          when :pub_sub
            Registrations::PubSub.new(topic: topic, path: path, fields: fields,
              metafield_namespaces: metafield_namespaces, filter: filter)
          when :event_bridge
            Registrations::EventBridge.new(topic: topic, path: path, fields: fields,
              metafield_namespaces: metafield_namespaces, filter: filter)
          when :http
            unless handler
              raise Errors::InvalidWebhookRegistrationError, "Cannot create an Http registration without a handler."
            end

            Registrations::Http.new(topic: topic, path: path, handler: handler,
              fields: fields, metafield_namespaces: metafield_namespaces, filter: filter)
          else
            raise Errors::InvalidWebhookRegistrationError,
              "Unsupported delivery method #{delivery_method}. Allowed values: {:http, :pub_sub, :event_bridge}."
          end
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L58-86)
```ruby
        def register(topic:, session:)
          return mandatory_registration_result(topic) if mandatory_webhook_topic?(topic)

          registration = @registry[topic]

          unless registration
            raise Errors::InvalidWebhookRegistrationError, "Webhook topic #{topic} has not been added to the registry."
          end

          client = Clients::Graphql::Admin.new(session: session)
          register_check_result = webhook_registration_needed?(client, registration)

          registered = true
          register_body = nil

          if register_check_result[:must_register]
            register_body = send_register_request(
              client,
              registration,
              register_check_result[:webhook_id],
            )
            registered = registration_sucessful?(
              register_body,
              registration.mutation_name(register_check_result[:webhook_id]),
            )
          end

          RegisterResult.new(topic: topic, success: registered, body: register_body)
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

### Title
Webhook metadata (`topic`/`shop`) is trusted without being covered by the HMAC signature, allowing forged-header replay of validly-signed bodies - (`lib/shopify_api/webhooks/registry.rb`)

### Summary
`Registry.process` only validates that the request body's HMAC matches (`Utils::HmacValidator.validate(request)`), but the signable string used for that HMAC is exclusively the raw body [1](#0-0) . The `topic` and `shop` values passed to the handler come straight from attacker-controllable HTTP headers and are never cross-checked against the signed body or against Shopify's actual delivery metadata [2](#0-1) . An attacker who legitimately receives one webhook (body+HMAC) from Shopify for their own dev shop can replay that exact body/HMAC pair to the app's shared webhook endpoint while swapping the `x-shopify-shop-domain` and/or `x-shopify-topic` headers, and `Registry.process` will accept it as authentic.

### Finding Description
The broken binding is: `HmacValidator.validate(request) == true` is treated as implying `request.shop` and `request.topic` are trustworthy, i.e. `valid_hmac(raw_body) ⇒ (topic, shop) are authentic`. That implication does not hold, because:

- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `topic`, `shop-domain`, `webhook-id`, and `api-version` headers are excluded from the HMAC computation.
- `Registry.process` raises `Errors::InvalidWebhookError` only when the HMAC over the body fails; once it passes, `request.topic` and `request.shop` are read directly from headers and passed unchecked into `WebhookMetadata` for the handler to consume [3](#0-2) .
- `HmacValidator.validate` itself only compares `verifiable_query.hmac` against a signature computed over `verifiable_query.to_signable_string` — it has no knowledge of, and never touches, `topic` or `shop` [4](#0-3) .

Exploit flow: the attacker (an ordinary developer) creates their own development shop, installs the target app, and registers a webhook for a topic of their choosing (e.g. one whose body content they can influence, such as `products/create`). Shopify delivers a genuinely-signed `(raw_body, hmac)` pair to the app's public webhook endpoint. Because the registered `path` is the same route for every shop using the app (registration is keyed by topic in the gem's registry, not by shop) [5](#0-4) , the attacker knows the exact URL. The attacker then re-POSTs the identical `raw_body` and `x-shopify-hmac-sha256` value to that same endpoint, but substitutes `x-shopify-shop-domain` with a victim shop's domain (and/or a different `x-shopify-topic`). `HmacValidator.validate` still succeeds because it only checks the untouched body, and `Registry.process` calls the handler with `WebhookMetadata` carrying the forged `shop`/`topic` and the attacker's original body content.

No other guard in this file (or in `Request`) cross-checks `topic`/`shop` against anything derived from the signed body, so this forged, cross-tenant-labeled webhook is accepted end-to-end.

### Impact Explanation
Any handler that uses `WebhookMetadata#shop` to key per-merchant logic (a standard pattern — persisting or acting on data "for shop X") will act on attacker-supplied body content while believing it originated from a different, victim merchant. This is a forged webhook being accepted as authentic, which the audit's severity table classifies as Critical ("authentication bypass — forged webhook … accepted"); at minimum it is a High-severity authorization/binding bypass since the topic/shop metadata that host applications rely on for scoping is never actually authenticated. The blast radius spans all merchants using the same app instance, since the webhook endpoint and registry are shared across shops [6](#0-5) . The attack is repeatable against arbitrary victim shop domains (which are typically guessable/known `*.myshopify.com` names) with a single captured valid body/HMAC pair reusable for any target shop label.

### Likelihood Explanation
Preconditions are exactly the unprivileged attacker profile described: create a dev shop, install the app, register/receive one genuine webhook. No `api_secret_key`, access token, or any credential is needed — only knowledge of the shared webhook endpoint URL, which the attacker learns for free the moment Shopify delivers their own webhook to it. The cost is a single legitimate webhook subscription and one crafted HTTP replay; this is trivially repeatable and requires no special app configuration beyond the gem being used as documented (`docs/usage/webhooks.md`'s example just forwards `request.raw_post`/headers directly into `Registry.process`) [3](#0-2) .

### Recommendation
Bind the authenticated body to the claimed metadata before trusting it: either include `topic` and `shop` in the HMAC-signable string (breaking compatibility with Shopify's current signing scheme, so likely not viable), or require callers to independently verify that `request.shop` matches an actual installed/authorized session for that shop before invoking the handler, and that `request.topic` matches a topic that was actually registered for that shop (e.g. via a stored mapping of shop→subscribed topics rather than trusting the header). At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be used as an authorization boundary without an additional shop-authenticity check by the host application.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (new test)
def test_process_accepts_forged_shop_and_topic_with_valid_body_hmac
  # Genuine signature computed only over the raw body, as Shopify would send it
  # for the attacker's own shop/topic.
  hmac = OpenSSL::HMAC.digest(
    OpenSSL::Digest.new("sha256"),
    ShopifyAPI::Context.api_secret_key,
    "{}",
  )

  # Attacker captures this real (body, hmac) pair from their own dev shop's
  # delivery, then replays it with forged shop/topic headers.
  forged_headers = {
    "x-shopify-topic" => "customers/data_request", # forged: not what was signed for
    "x-shopify-hmac-sha256" => Base64.encode64(hmac), # unchanged, still valid for "{}"
    "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  }

  handler_called_with = nil
  handler = TestHelpers::FakeWebhookHandler.new(
    lambda { |data| handler_called_with = data },
  )

  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "customers/data_request", path: "path", delivery_method: :http, handler: handler,
  )

  request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)

  # No InvalidWebhookError is raised, despite shop/topic being unverified against the body.
  ShopifyAPI::Webhooks::Registry.process(request)

  assert_equal("victim-shop.myshopify.com", handler_called_with.shop)
end
```
This demonstrates that `Registry.process` accepts a request whose `shop`/`topic` headers were mutated after signing, with the body/HMAC pair unchanged, confirming no secondary consistency check exists between the authenticated body and the trusted metadata.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

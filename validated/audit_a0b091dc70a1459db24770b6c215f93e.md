### Title
Webhook shop identity derived from unsigned headers while only the body is HMAC-verified - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which only verifies `request.to_signable_string` (the raw body) against the received HMAC, then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id`, all of which come from HTTP headers that are never included in the signed payload. Because the signature binds only the body, any request that reproduces a previously-obtained valid `(body, hmac)` pair can carry arbitrary headers — including a different `shop-domain` — into the handler.

### Finding Description
The binding the invariant requires is: `shop_identity_used_by_handler == shop_identity_covered_by_hmac`. Tracing the code shows this never holds because the two values come from disjoint sources.

`Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `shop`, `topic`, `webhook_id`, and `api_version` are all read from `@headers` via `shopify_header` [2](#0-1) . `HmacValidator.validate_signature` computes the HMAC strictly over `verifiable_query.to_signable_string` [3](#0-2) , so the headers never enter the signature computation.

`Registry.process` uses this validation result as a gate, then immediately forwards the unverified header-derived values (`request.topic`, `request.shop`, `request.webhook_id`, `request.api_version`) straight into `WebhookMetadata` and the handler [4](#0-3) . There is no check anywhere in this path that ties `shop` (or any other header) to the body content or to the HMAC computation.

Exploit flow: an attacker registers their own development shop and their own webhook endpoint, so Shopify sends them a validly-signed `(body, X-Shopify-Hmac-Sha256)` pair for a legitimate topic on their own shop. Because the app's webhook route is public, the attacker can POST that exact `body` and `hmac` directly to the victim app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (and, if desired, `X-Shopify-Webhook-Id`) with the victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body/HMAC pair, which is unchanged and genuinely valid. `process` then builds `WebhookMetadata` with `shop: <victim-domain>` and hands it to the handler, which will treat the attacker's body as authentic data belonging to the victim shop.

Existing guards do not stop this: `HmacValidator.validate` [5](#0-4)  only re-derives the signature from the body; `Request#initialize` only checks header *presence*, not header/body correspondence [6](#0-5) ; there is no `ShopValidator.sanitize!`, session, or JWT check anywhere in `process`.

Note: the "fast validation" hint referencing `get_webhook_id` and GraphQL-metacharacter injection is not part of this reachable path — `get_webhook_id` is only invoked from `unregister`, which requires a pre-authenticated `Auth::Session` obtained through the OAuth flow, not from `process`'s public webhook route [7](#0-6) . That specific sub-claim does not hold; the substantive, reachable defect is the header/body decoupling described above.

### Impact Explanation
An attacker with their own valid webhook credential stream can cause a merchant app to process webhook payloads under an arbitrary victim shop's identity (`request.shop`), because that value is taken from an unauthenticated header rather than from anything the HMAC covers. Depending on the handler's trust in `WebhookMetadata#shop` (commonly used to look up the shop's stored session/access token or to write shop-scoped data), this enables cross-tenant data corruction or shop impersonation inside the handler — matching "cross-tenant access" / forged-webhook acceptance. This is repeatable against any victim shop domain the attacker chooses to put in the header, for every webhook topic the attacker can get validly signed for their own shop.

### Likelihood Explanation
Preconditions are minimal and within the attacker capability set defined by the rules: attacker needs only their own development shop, an app installed on it, and a registered webhook endpoint to legitimately receive one valid `(body, hmac)` pair from Shopify. No `api_secret_key` or session material is required. The only cost is capturing one legitimately signed webhook and replaying it with a modified `shop-domain` header to the target app's public webhook endpoint. Whether it is exploitable in practice depends entirely on how the specific app's handler uses `WebhookMetadata#shop` (e.g., to fetch stored credentials) — the gem provides no mitigation regardless of handler behavior.

### Recommendation
Do not trust `request.shop`/other headers as authenticated identity derived independently of the signed payload. At minimum, document that `WebhookMetadata#shop` is unauthenticated relative to the HMAC and must be cross-checked by the handler against the shop under which the topic/webhook subscription was registered, or extend the signable string / verification step to bind the `shop-domain` and `topic` headers into the HMAC check (mirroring how Shopify's platform associates a specific webhook subscription id with a specific shop) before constructing `WebhookMetadata`.

### Proof of Concept
Minitest sketch under `test/webhooks/registry_test.rb` style, using WebMock/Mocha, no live shop:
```ruby
def test_process_trusts_shop_header_independent_of_hmac
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)

  raw_body = '{"id": 123, "note": "attacker shop data"}'
  valid_hmac = Base64.encode64(
    OpenSSL::HMAC.digest("sha256", "secret", raw_body)
  ).strip

  # headers claim a DIFFERENT shop than the one the body/hmac actually belongs to
  headers = {
    "X-Shopify-Topic" => "orders/create",
    "X-Shopify-Hmac-Sha256" => valid_hmac,
    "X-Shopify-Shop-Domain" => "victim-shop.myshopify.com",
    "X-Shopify-Api-Version" => "2024-01",
    "X-Shopify-Webhook-Id" => "forged-id",
  }
  request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

  handler = Minitest::Mock.new
  handler.expect(:handle, nil) do |data:|
    data.shop == "victim-shop.myshopify.com" # attacker-controlled, yet HMAC-validated
  end
  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: "orders/create", delivery_method: :http, path: "/x", handler: handler
  )

  ShopifyAPI::Webhooks::Registry.process(request) # does not raise despite spoofed shop header
  handler.verify
end
```
Assert both sides of the binding: `Utils::HmacValidator.validate(request)` returns `true` (body/hmac genuinely match) while `request.shop` equals an attacker-chosen value never covered by that HMAC — demonstrating `shop_identity_used_by_handler != shop_identity_covered_by_hmac`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L123-154)
```ruby
        def unregister(topic:, session:)
          return { "response": nil } if mandatory_webhook_topic?(topic)

          client = Clients::Graphql::Admin.new(session: session)

          webhook_id = get_webhook_id(topic: topic, client: client)
          return {} if webhook_id.nil?

          delete_mutation = <<~MUTATION
            mutation webhookSubscription {
              webhookSubscriptionDelete(id: "#{webhook_id}") {
                userErrors {
                  field
                  message
                }
                deletedWebhookSubscriptionId
              }
            }
          MUTATION

          delete_response = client.query(query: delete_mutation, response_as_struct: false)
          raise Errors::WebhookRegistrationError,
            "Failed to delete webhook from Shopify" unless delete_response.ok?
          result = T.cast(delete_response.body, T::Hash[String, T.untyped])
          errors = result["errors"] || {}
          raise Errors::WebhookRegistrationError,
            "Failed to delete webhook from Shopify: #{errors[0]["message"]}" unless errors.empty?
          user_errors = result.dig("data", "webhookSubscriptionDelete", "userErrors") || {}
          raise Errors::WebhookRegistrationError,
            "Failed to delete webhook from Shopify: #{user_errors[0]["message"]}" unless user_errors.empty?
          result
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

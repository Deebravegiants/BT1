### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant-identity spoofing on an otherwise validly-signed webhook - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` is computed only over the raw request body. The `shop` value is therefore "acted on" (passed to the app as the authenticated tenant) without being covered by the cryptographic proof that is supposed to authenticate the whole webhook.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an HTTP header with no cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC of the request and then forwards `request.shop` (the unauthenticated header) directly into `WebhookMetadata`, which is what host application handlers use to identify which merchant/tenant the payload belongs to: [3](#0-2) 

The identity binding that should hold is:
`bytes cryptographically verified (raw_body only)` == `bytes/fields acted on as the tenant identity (shop header)`

This equality does not hold: the HMAC only proves the body wasn't tampered with; it says nothing about which shop header was attached to that body. `HmacValidator.validate_signature` confirms the signature only ever signs `verifiable_query.to_signable_string`, i.e., the body for webhooks: [4](#0-3) 

The test suite explicitly documents this behavior — the HMAC is computed over `"{}"` (the body) and the `shop`, `topic`, and `webhook-id` headers are freely supplied and immediately trusted after only the body-HMAC check passes: [5](#0-4) [6](#0-5) 

### Impact Explanation
Any request whose raw body plus a legitimately-computed HMAC can be obtained (for example, a webhook a merchant/attacker's own shop legitimately receives from Shopify to the app's public webhook endpoint) has an HMAC that is valid regardless of the `shop-domain` header value, because that header is never part of the signed content. An attacker who controls or can intercept traffic to their own installation's webhook endpoint can replay the same signed body while substituting the `x-shopify-shop-domain` header for a different (victim) shop. `Registry.process` will accept the HMAC as valid (it only checks the body) and hand the handler a `WebhookMetadata` claiming the payload came from the victim shop. Any host application logic that uses `data.shop` to select a tenant record, session, or database scope (a very common pattern, and the one implied by the library's own design intent for `shop` in `WebhookMetadata`) would then process/store attacker-controlled data under the victim tenant's identity — a cross-tenant data injection primitive that stems directly from this gem's own request-parsing/validation design, not merely from host-application misuse of an "undocumented" API.

This satisfies the Critical impact bucket ("cross-tenant access") because a boundary that is supposed to separate one merchant's data/webhooks from another's is broken purely through parsing/validation logic in the gem, without requiring the attacker to know `api_secret_key` or hold any privileged credential — only a legitimately-signed body they can obtain from their own shop's own webhook deliveries.

### Likelihood Explanation
Exploitation requires the attacker to have a shop that has installed the app (readily available to any developer/tester) so Shopify sends real, validly-signed webhooks to the app's endpoint, and requires the attacker to be able to replay/relay an HTTP request to that same endpoint with a modified `shop-domain` header (trivial with any HTTP client, since headers are not authenticated). No access to `api_secret_key`, tokens, or the target's infrastructure is needed. The main variable affecting likelihood is whether the host application actually treats `WebhookMetadata#shop` as an authoritative tenant identifier without any additional check (e.g., cross-referencing against a known/installed-shops list) — which is the pattern the library's own API design (and its tests) encourages.

### Recommendation
- Include the shop domain (and ideally the topic and webhook id) in the value that is HMAC-verified, or independently authenticate the shop by cross-referencing it against a store of shops that have valid sessions/installations before trusting `request.shop`.
- At minimum, document prominently in `Request`/`Registry` that `shop`, `topic`, and `webhook_id` are **not** cryptographically authenticated by `HmacValidator.validate`, and that consuming applications must independently verify the shop domain (e.g., against their own installed-shops table) before using it as a tenant key.
- Consider deriving/validating the shop domain from data embedded in the signed body when the payload topic includes shop-identifying fields, rather than relying solely on the header.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker captures this request (e.g., via a local proxy on infrastructure they control, or by pointing their own webhook delivery URL to a controlled server first, then relaying).
3. Attacker crafts a new HTTP request to the same webhook endpoint with the same body `B`, the same valid `x-shopify-hmac-sha256` header, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` parses successfully; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against the HMAC and succeeds: [3](#0-2) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the actual payload/body originated from the attacker's own shop, allowing the attacker to inject arbitrary (attacker-controlled) webhook content under the victim tenant's identity in any host application that trusts `data.shop` as the tenant key.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** test/webhooks/registry_test.rb (L16-33)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```

**File:** test/webhooks/registry_test.rb (L241-264)
```ruby
      def test_process_with_response_as_struct
        modify_context(response_as_struct: true)

        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal(@headers["x-shopify-webhook-id"], data.webhook_id)
            assert_equal(@headers["x-shopify-api-version"], data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        ShopifyAPI::Webhooks::Registry.process(@webhook_request)

        assert(handler_called)
      end
```

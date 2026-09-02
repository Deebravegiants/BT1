### Title
Webhook HMAC Signature Does Not Cover the `shop`/`topic`/`webhook_id` Headers, Enabling Cross-Tenant Webhook Spoofing via Replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `Utils::HmacValidator` verifies binds nothing but the JSON payload bytes. The `shop-domain`, `topic`, and `webhook-id` headers — which `Registry.process` trusts to identify the tenant and route the payload — are never included in the signed material. Any actor who has legitimately received one valid `(body, hmac)` pair for the app (e.g. a merchant who has installed the app themselves) can replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header for another shop, and the signature check still passes.

### Finding Description
`HmacValidator.validate` computes the expected signature purely from `verifiable_query.to_signable_string` and compares it against the `hmac` field: [1](#0-0) 

For webhook requests, `to_signable_string` is defined to return only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` that is handed to the app's handler, with no additional binding check between the signed body and the header-derived shop: [3](#0-2) 

Because the shop identity is carried in a header that is outside the signed scope, the equality the code implicitly assumes — `hmac_is_valid(body) == shop_header_is_authentic` — does not hold. `hmac_is_valid(body)` only proves the body bytes were signed with the app's secret at some point; it says nothing about which shop that signature was originally issued for. The test suite even demonstrates the header/body decoupling directly, confirming `shop`, `topic`, and `webhook_id` are independent of the signed value: [4](#0-3) 

### Impact Explanation
A merchant who has installed the app receives their own legitimately signed webhooks (valid `raw_body` + `x-shopify-hmac-sha256` pairs) as a normal, unprivileged part of using the app — no `api_secret_key`, access token, or credential theft is required. That merchant can resend the exact same body/HMAC pair to the app's public webhook endpoint while swapping only the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to point at a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspected those headers, so `Registry.process` dispatches the forged webhook to the handler tagged with the victim's shop. Depending on how the host app keys its webhook handling logic on `WebhookMetadata#shop` (e.g. updating billing state, toggling `app/uninstalled` cleanup, mutating order/inventory records, or driving anything keyed by shop), this allows a low-privilege tenant to inject attacker-controlled, falsely-attributed events into another tenant's data path — a cross-tenant integrity/access violation stemming directly from this gem's signature-binding gap.

### Likelihood Explanation
Any app that uses this gem's webhook processing is affected, and the pre-condition is minimal: the attacker only needs to be a normal, self-service installer of the target app (extremely common for public/multi-tenant Shopify apps) and needs no access to `api_secret_key`, tokens, or any Shopify-internal system. Capturing their own webhook `(body, hmac)` pair and replaying it with a different shop header is trivial with any HTTP client.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the shop/topic to the payload before trusting them in `Registry.process`. At minimum, `WebhookMetadata`'s `shop` should be cross-checked against a value that is actually covered by the HMAC (for example, deriving/confirming shop identity from data embedded in the signed body, or requiring TLS-terminated, Shopify-verified delivery metadata) rather than an unauthenticated header.

### Proof of Concept
1. App merchant "attacker.myshopify.com" installs the target Shopify app and receives a legitimate webhook delivery:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-raw-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: abcd-1234

   { ...raw_body... }
   ```
2. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` value, only changing the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac-for-raw-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: abcd-1234

   { ...raw_body... }
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC as shown in `lib/shopify_api/utils/hmac_validator.rb` lines 12-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38.
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, i.e., attacker-controlled data falsely attributed to a shop the attacker does not own, as wired in `lib/shopify_api/webhooks/registry.rb` lines 188-200.

### Citations

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

**File:** test/webhooks/registry_test.rb (L266-302)
```ruby
      def test_process_with_new_format_headers
        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal("b1234-eefd-4c9e-9520-049845a02082", data.webhook_id)
            assert_equal("2024-01", data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)

        assert(handler_called)
      end
```

### Title
Webhook shop identity spoofing via HMAC that only covers the request body, not the shop/topic/webhook-id headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified by `ShopifyAPI::Webhooks::Registry.process` never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. Any party who can obtain one legitimately-signed webhook body (e.g. by installing the app on their own shop) can replay that exact body to a target app's webhook endpoint while freely rewriting the `X-Shopify-Shop-Domain` header to a victim shop, and the gem will report the request as validly authenticated.

### Finding Description
`Request#hmac`/`#to_signable_string` are the only two members of the `VerifiableQuery` interface that `HmacValidator.validate` uses to authenticate a webhook: [1](#0-0) 

`to_signable_string` returns `@raw_body` alone — none of the Shopify-supplied headers (`shop`, `topic`, `webhook_id`, `api_version`) are folded into the signed string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string`, i.e. purely from the body: [3](#0-2) 

Yet `Registry.process` trusts `request.shop`, `request.topic`, and `request.webhook_id` — all attacker-controllable headers — as soon as the (body-only) HMAC check passes, and forwards them unchanged to the app's registered handler as the tenant identity for the event: [4](#0-3) 

The equality the code implicitly assumes is:
`HMAC_valid(body, api_secret_key) == true` ⇒ `shop-domain header is the true origin shop of body`

That equality does not hold: `HMAC_valid` only proves the body was produced/forwarded using the app's shared `api_secret_key` (true for *any* shop that has the app installed, including one the attacker controls) — it says nothing about which shop header accompanies it. Because a public app's `api_secret_key` is identical across every merchant installation, a user who installs the app on their own shop can:
1. Trigger a real webhook delivery to their own endpoint (e.g. `orders/create`), capturing the raw body and its valid `X-Shopify-Hmac-Sha256` value.
2. Replay that exact `(body, hmac)` pair to the app's webhook endpoint, substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `HmacValidator.validate` recomputes the same HMAC over the same body with the same shared secret and it matches, so `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: attacker's body, ...)`.

The test suite confirms `Registry.process` propagates the header-derived `shop` verbatim into the handler without any additional binding check: [5](#0-4) 

### Impact Explanation
Applications using `ShopifyAPI::Webhooks::Registry` (the gem's own documented webhook-processing entry point) typically use `WebhookMetadata#shop` to look up/mutate per-tenant state (e.g. the merchant record, cached settings, order records, or to decide whether to revoke access on `app/uninstalled`). Since the shop identity is not bound to the HMAC, an attacker who is merely a legitimate but unprivileged installer of the app on their own shop can inject attacker-controlled webhook payloads that the host application will process as belonging to any other shop of their choosing — a cross-tenant data injection/confusion that can corrupt or manipulate another merchant's tenant state (e.g., forging an `app/uninstalled` event to trigger de-provisioning of a victim's data, or injecting fabricated `orders/create`/`customers/create` payloads attributed to the victim).

### Likelihood Explanation
Requires no leaked credentials, no TLS interception, and no privileged account — only the ability to install the app on one's own shop (or otherwise obtain a single validly-signed webhook body/HMAC pair) and to POST to the app's public webhook endpoint with attacker-chosen headers. This is squarely within the "unprivileged internet user" threat model for public multi-tenant apps built on this gem.

### Recommendation
Bind the identity headers into the signed content that `HmacValidator` verifies — e.g. include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (matching them against a canonical, out-of-band record such as a previously-registered webhook subscription for that shop), or otherwise require the app to independently verify that `request.shop` corresponds to a shop for which the specific `webhook_id`/subscription was actually registered before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the target Shopify app on an attacker-owned development shop, `attacker.myshopify.com`.
2. Trigger any webhook subscribed by the app (e.g., create an order) and capture the raw POST body `B` and its `X-Shopify-Hmac-Sha256: H` header sent to the app's webhook URL.
3. Send a new POST request to the same webhook URL with:
   - Body = `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic`/`X-Shopify-Webhook-Id` set arbitrarily.
4. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` (body+secret unchanged), so `ShopifyAPI::Webhooks::Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, processing attacker data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

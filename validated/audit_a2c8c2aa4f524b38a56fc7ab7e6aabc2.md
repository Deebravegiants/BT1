### Title
Webhook HMAC Only Covers the Request Body, Not the `shop`/`topic`/`webhook-id` Headers, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` accepts a webhook only after `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only covers the raw JSON body. The `shop`, `topic`, `webhook_id`, and `api_version` values that the handler subsequently trusts and acts on are read straight from unauthenticated HTTP headers and are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are not part of that signable string: [2](#0-1) 

`Registry.process` verifies the HMAC and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute the digest solely from `verifiable_query.to_signable_string` (the body) and the app's single, shop-independent `api_secret_key`: [4](#0-3) 

Since `api_secret_key` is one shared secret for the whole app across every installed shop, and the signature never binds to `shop`/`topic`/`webhook_id`, any party that receives one legitimate webhook delivery (e.g., by installing the app on their own store) can replay that exact `(raw_body, hmac)` pair to the same endpoint while forging the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers. Many Shopify webhook topics (e.g., shop-level lifecycle events) use a static/predictable body such as `"{}"`, as shown in this repo's own test fixtures: [5](#0-4) 

The equality that should hold is: **shop asserted by the HMAC-verified payload == shop the handler acts on**. Here, the HMAC only proves "produced with the app's secret" and says nothing about which shop or topic it belongs to, so the equality is broken — `request.shop`/`request.topic` are trusted despite being outside the authenticated boundary.

### Impact Explanation
This breaks the tenant boundary: an attacker who is merely a legitimate merchant of one shop that has installed the app (i.e., an "unprivileged" tenant relative to other merchants) can cause the host application's webhook handler to execute business logic attributed to an arbitrary other shop (`shop` header) and/or an arbitrary topic (`topic` header), using a body they captured from their own legitimate delivery. Depending on what the host app's handlers do (e.g., uninstall cleanup, data deletion/redaction, entitlement changes keyed by `shop`), this is a cross-tenant access/action vulnerability — the app cannot distinguish "genuinely delivered for shop X" from "replayed and relabeled as shop X."

### Likelihood Explanation
Requires only that the attacker operate one shop with the app installed (no privileged access, no leaked secret, no TLS interception) and capture one webhook delivery with a body that is static or otherwise predictable/reusable across shops/topics — a realistic scenario given several Shopify webhook payloads are empty (`{}`) or highly predictable.

### Recommendation
Bind the shop/topic/webhook identity into the verified signature surface, or otherwise cryptographically/contextually tie the header-derived `shop` to the expected shop before dispatching to handlers — e.g., compare `request.shop` against the shop associated with the currently-processing session/subscription, or require the caller to supply the expected shop out-of-band and assert equality before invoking `handler.handle`. At minimum, document that `Registry.process` callers must independently verify `request.shop` matches an expected/authorized shop, since the HMAC does not guarantee it.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook topic whose payload body is `{}` (e.g., many shop-level events) and capture the raw `POST` body and the `x-shopify-hmac-sha256` header Shopify sends.
2. Replay that exact HTTP request to the app's webhook endpoint, but replace headers:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: <any topic registered by the app with an equivalent-body payload>`
   - keep the original `x-shopify-hmac-sha256` and body `{}` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over the body `{}` with the shared `api_secret_key` and succeeds, since body/secret are unchanged, per: [6](#0-5) 
4. The app's handler now executes as though `victim.myshopify.com` sent the event of the attacker's choosing.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** test/webhooks/registry_test.rb (L14-33)
```ruby
        @shop = "shop.myshopify.com"

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

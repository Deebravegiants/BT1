This confirms the root cause: `HmacValidator.validate` for webhooks signs and verifies only `@raw_body` via `to_signable_string` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC and then hands the handler a `WebhookMetadata` built from `request.shop` (the unverified header) without any additional binding to the signed content [3](#0-2) .

### Title
Webhook `shop-domain` (and topic/webhook-id) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Utils::HmacValidator.validate` authenticates a webhook solely by recomputing the HMAC over `to_signable_string`, which for `Webhooks::Request` returns only the raw JSON body [1](#0-0) . The `shop`, `topic`, and `webhook_id` values used downstream by the handler come from HTTP headers that are never part of the signed content [2](#0-1) . This is the same bug class as the referenced report: a value that is acted upon (`shop`) is not bound by the cryptographic check that is supposed to authenticate the whole request (`hmac` over `to_signable_string`), so the two "unit"/scopes don't match, an equality the code implicitly assumes but never enforces.

### Finding Description
`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` header using `OpenSSL.secure_compare` [4](#0-3) . For webhooks, `to_signable_string` is defined as just `@raw_body` [1](#0-0) , whereas `shop`, `topic`, and `webhook_id` are pulled from headers (`shopify_header`) that are completely outside the signed scope [5](#0-4) .

`Registry.process` uses this same unverified `request.shop` when constructing the `WebhookMetadata` passed to the app's handler: it checks `Utils::HmacValidator.validate(request)` (which only validates the body) and then dispatches `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [3](#0-2) . Because the signature never covers `shop`/`topic`/`webhook_id`, any HMAC value that is valid for a given raw body remains valid no matter what `shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` header values accompany it.

Any multi-tenant app built on this gem receives real, validly-signed webhooks from Shopify for every shop that installs it (this happens through completely legitimate app installation - no `api_secret_key`, access token, or privileged account needed on the attacker's part, since Shopify itself computes and sends the signature for the attacker's own shop). Because many webhook topics carry small, fixed, or attacker-controllable bodies (e.g. `{}` for topics without dynamic payload, as used in this repo's own test fixtures [6](#0-5) ), the attacker, having installed the app on their own shop, can capture one genuine `(raw_body, hmac)` pair from a webhook delivered to their own endpoint and then replay that same body+HMAC to the app's shared webhook endpoint while substituting the `shop-domain` header of a victim tenant. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will happily deliver a `WebhookMetadata` claiming to be from the victim's `shop` to the handler.

This breaks the intended identity binding: `authenticated_shop == shop_the_handler_believes_sent_this_event` no longer holds, because the left side is never checked at all — only the body is authenticated, not the shop claim.

### Impact Explanation
This is a cross-tenant webhook forgery: an attacker who legitimately installs the app on their own shop (no privileged credentials beyond that) can trick an app into believing an event (e.g. `app/uninstalled`, `shop/redact`, `customers/redact`, or any topic whose payload happens to be small/predictable) originated from a different, victim shop. Depending on what the host application does with `WebhookMetadata#shop` (e.g. deleting/deactivating the victim's stored session/access token on `app/uninstalled`, purging victim data on `shop/redact`, or triggering other per-tenant side effects), this can cause cross-tenant data manipulation or denial of the victim's app functionality — matching the "High: cross-tenant access" impact category, since a value trusted as the tenant identity is not bound by the same proof that authenticates the request.

### Likelihood Explanation
Likelihood is moderate to high in any deployment where: (1) the same app (and thus the same `api_secret_key`) serves multiple shops, which is the standard SaaS/Shopify-app model this gem is built for, and (2) at least one webhook topic in use has a body that is constant or guessable across shops (several Shopify webhook topics, including mandatory compliance topics, can have minimal or predictable bodies). An attacker only needs to install the app once on a shop they control to obtain one valid `(body, hmac)` pair.

### Recommendation
Include the identity-binding fields in the signed content, or otherwise cryptographically bind `shop`, `topic`, and `webhook_id` to the HMAC check rather than trusting them as raw headers. Concretely, change `Webhooks::Request#to_signable_string` to incorporate `shop`, `topic`, and `webhook_id` (e.g., a canonicalized concatenation of body + shop + topic + webhook_id) so `HmacValidator.validate` cannot succeed unless all of these values match what Shopify actually signed, closing the gap between "bytes verified" and "identity fields acted on."

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`. Trigger a webhook topic whose body is small/fixed (e.g. one that Shopify sends with body `{}`), capturing the raw body and the `X-Shopify-Hmac-Sha256` header Shopify computed with the app's real `api_secret_key`.
2. Replay an HTTP POST to the app's webhook endpoint using the identical raw body and `X-Shopify-Hmac-Sha256` value captured in step 1, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and desired `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`. `Utils::HmacValidator.validate(request)` succeeds because it only checks the raw body against the HMAC [7](#0-6) , and the handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the signature never certified that shop value [8](#0-7) .

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

**File:** test/webhooks/registry_test.rb (L284-299)
```ruby
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
```

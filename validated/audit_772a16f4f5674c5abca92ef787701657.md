This confirms the vulnerability shape. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` bind the HMAC solely to `@raw_body`, while `#shop` (`Webhooks::Registry.process` → `WebhookMetadata.new(shop: request.shop, ...)`) is read from an unsigned header, and `Registry.process` never checks it against the topic's expected/registered shop. Since the app's `api_secret_key` is shared across every shop installation of the app (not shop-specific), any tenant that has legitimately installed the app can compute a valid HMAC over an arbitrary JSON body they choose, then submit it to the app's webhook endpoint with `X-Shopify-Shop-Domain` set to a different (victim) shop. `Utils::HmacValidator.validate` only checks the body↔signature relationship and passes, and the handler receives `WebhookMetadata` attributing attacker-chosen `topic`/`body` to the victim shop. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook HMAC Signs Only the Raw Body, Not the Shop Identity — Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity with `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string` — the raw JSON body only. The shop identity (`request.shop`), which is passed on to the app's handler as the tenant context (`WebhookMetadata#shop`), comes from the `X-Shopify-Shop-Domain` header and is never included in the signed material and never cross-checked. Because the same app-wide `api_secret_key` is used to validate webhooks from every shop that has installed the app, any shop that is (or was) a legitimate installer of the app can produce a validly-signed body and re-submit it with a different shop domain header, and the library will report it to the handler as if it came from that other shop.

### Finding Description
- `Webhooks::Request#hmac` decodes the `hmac-sha256`/`x-shopify-hmac-sha256` header, and `#to_signable_string` returns `@raw_body` verbatim. [5](#0-4)  Neither the topic nor the shop-domain header contributes to the signed string.
- `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, to_signable_string)` and compares it with the provided `hmac`. [6](#0-5)  `api_secret_key` is a single app-wide secret (`Context.api_secret_key`), identical for every shop that installed the app — it is not shop-specific.
- `Registry.process` uses only this body-bound HMAC check as its authenticity gate, then builds `WebhookMetadata` from `request.shop`, `request.topic`, and `request.parsed_body` without any additional binding between the signature and the shop/topic values. [3](#0-2) 
- The binding that should hold is: `shop_the_signature_was_issued_for == shop_attributed_to_the_request`. In reality the check only proves `body_bytes_verified == body_bytes_parsed`; it says nothing about which shop the signature is "for," because the signature never depended on the shop at all.
- Exploit path: an attacker installs the target app on their own (attacker-controlled) shop — a normal, unprivileged action any Shopify merchant can take. Shopify will then deliver genuine, validly HMAC-signed webhooks for that attacker shop to the app's webhook endpoint. The attacker captures one such `(raw_body, hmac)` pair (or crafts any JSON body and computes the HMAC themselves, since they know the exact bytes that will be sent are attacker-controlled — e.g. via a webhook whose editable fields they control, such as `note` on an order they place), then POSTs it again to the same endpoint, but swaps `X-Shopify-Shop-Domain` to the victim shop's domain. `Registry.process` still validates because the HMAC only ever depended on the (unchanged) body, not the header.

### Impact Explanation
This crosses a tenant boundary: an app whose webhook handler makes tenant-scoped decisions keyed off `WebhookMetadata#shop` (e.g., updating billing state, order/inventory records, GDPR redaction flags, or feature flags for "that shop") can be made to apply attacker-controlled webhook data to a shop the attacker does not control and never authorized. Because `shop/redact` and `customers/redact`/`customers/data_request` are also delivered through this same unauthenticated-shop path, an attacker can potentially trigger data-redaction or data-request side effects the app performs "for" a victim shop. This satisfies the High-severity bar of credential/tenant boundary violation (cross-tenant access) via a documented, intended API surface of the gem.

### Likelihood Explanation
Likelihood is high for any app that has: (1) more than one tenant/shop installed (trivial — any attacker can install the app on a shop they control to obtain valid signed traffic), and (2) a webhook handler that trusts `data.shop` for tenant attribution without an independent verification (the gem's own documentation instructs handlers to key work off `data.shop` directly, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`). No credentials, tokens, or privileged access are required — only the ability to install the app on an attacker's own shop and send arbitrary HTTP requests to the app's public webhook endpoint.

### Recommendation
Bind the shop domain (and ideally the topic) into the value that is authenticated, or otherwise verify that `request.shop` is a shop the app has an active session/installation for and that it matches the expected recipient before constructing `WebhookMetadata`. At minimum, `Registry.process` should validate `request.shop` against the app's known set of installed shops (or a per-shop secret/session) rather than relying solely on the app-wide HMAC over the body.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop (attacker-shop.myshopify.com),
#    a fully legitimate, unprivileged action.
# 2. Attacker triggers/receives (or crafts) a genuine webhook for their shop:
raw_body = '{"id":1,"note":"pwned"}'
hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# 3. Attacker resends the same signed body to the app's public webhook endpoint,
#    but swaps the shop-domain header to the victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by hmac
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body/signature match),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
#    is invoked with attacker-controlled body attributed to the victim shop.
``` [7](#0-6)

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

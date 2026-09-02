### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`) values that are dispatched to the host application's webhook handler are read directly from unauthenticated HTTP headers. The gem's `HmacValidator.validate` only proves that the *body* bytes were signed with the app's secret; it never binds the `shop-domain` header into that signature. An attacker who can obtain any one validly-signed `(body, hmac)` pair for the app can replay it to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the request still passes HMAC validation and is dispatched as if it originated from the spoofed shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
returning only `@raw_body`. Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from the request headers, uncovered by the signature: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e., the body, and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` trusts this validation result and then dispatches the handler using `request.shop`, which was never part of what was signed: [4](#0-3) 

This breaks the intended identity binding: `shop_authenticated_by_hmac == shop_dispatched_to_handler`. In reality the equality is `hmac_covers(body) == true` and `shop_dispatched = header["shopify-shop-domain"]` (attacker controlled), with no cryptographic linkage between the two. The test suite itself demonstrates the disconnect — the HMAC in `registry_test.rb` is computed only over the body `"{}"`, independent of whatever `shop` header value is supplied: [5](#0-4) 

### Impact Explanation
Any webhook topic whose body is generic, predictable, or reusable across shops (e.g., an empty JSON body `{}` for topics like `app/uninstalled`, `shop/redact`, or any payload an attacker can legitimately obtain by installing the app on their own store) yields a valid `(body, hmac)` pair signed with the app's real secret. The attacker can then POST that same body/hmac to the app's webhook endpoint while setting an arbitrary `shopify-shop-domain` header naming a victim shop. Because the shop value is not part of the signed payload, `Registry.process` will accept the forged request and invoke the handler with `WebhookMetadata` claiming the event is for the victim shop, causing the host application to perform actions (e.g., de-provisioning, data deletion, state changes) against a tenant the attacker does not control. This constitutes cross-tenant access/impact, matching the "Critical - cross-tenant access" category.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on a shop they control (a routine, unprivileged action) to obtain one legitimately-signed webhook body/HMAC pair, then replay it with a spoofed `shop-domain` header against the same public webhook endpoint. No access token, `api_secret_key`, or privileged credential is needed — only knowledge of the shop domain to spoof and a genuine `(body, hmac)` sample, both trivially obtainable by any developer/attacker who can install the app.

### Recommendation
Include the `shop` (and ideally `topic`/`api_version`) header values in the signed material used for HMAC verification, or otherwise cryptographically bind them to the request (e.g., verify the header-declared shop against a shop the app has stored as legitimately installed with a matching correlation established at OAuth time), so that a valid signature for one shop's payload cannot be replayed against another shop.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# receives (or triggers) a legitimate webhook, e.g. app/uninstalled with body "{}",
# capturing the real hmac header value computed by Shopify with the app's real secret:
#
#   x-shopify-hmac-sha256: <real_signature_for_body_"{}">
#
# Attacker now replays the exact same body + hmac header to the app's public
# webhook endpoint, but swaps the shop-domain header to a victim shop:

headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => captured_valid_hmac_for_empty_body, # signed for attacker's own shop
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",        # spoofed, NOT covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers)

# HmacValidator.validate only checks the body against the hmac -> passes
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The host app now believes victim-shop.myshopify.com triggered app/uninstalled.
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

**File:** test/webhooks/registry_test.rb (L16-31)
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
```

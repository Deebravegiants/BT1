### Title
Webhook `shop` (and `topic`/`webhook-id`) fields are trusted from unsigned headers while only the raw body is HMAC-covered, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), event type (`topic`), and other routing metadata from HTTP headers that are never included in the HMAC signature computation, while `ShopifyAPI::Webhooks::Registry.process` only validates the HMAC before handing these unverified fields to the app's handler. An attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`—for example by installing the app on their own store and capturing one of their own legitimately delivered webhooks—can replay that exact body/HMAC pair while freely substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version` headers to impersonate a different tenant or event type.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC of the request and then forwards the unverified header-derived fields directly to the registered handler as trusted metadata: [3](#0-2) 

`HmacValidator.validate` in turn only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the raw body), never the shop/topic headers: [4](#0-3) 

The broken binding is: `hmac == HMAC(api_secret_key, raw_body)` is verified, but the tenant-identifying claim `shop` (and `topic`/`webhook_id`) that the app acts on is not part of what's verified — i.e. `shop_acted_on != shop_covered_by_hmac` (the latter set is empty).

### Impact Explanation
Because only the raw body is signed, any unprivileged internet user who can trigger one legitimate webhook delivery to the app (trivially achievable by installing the app on a store they control, or observing/replaying any historic delivery of theirs) obtains a valid `(body, hmac)` pair for the app's `api_secret_key`. That pair remains valid regardless of which `shop-domain`/`topic`/`webhook-id` headers are sent alongside it, since `Registry.process` never binds these header values into the HMAC check. The attacker can therefore submit a request that Registry.process fully accepts (`InvalidWebhookError` is never raised) while attributing the body to an arbitrary victim shop and/or arbitrary topic (e.g. `shop/redact`, `app/uninstalled`), causing the app to execute tenant-scoped logic (data writes, deletions, session/token lookups) against the wrong tenant. This is a cross-tenant access primitive achievable purely with an internet-reachable webhook endpoint and no privileged credentials.

### Likelihood Explanation
High: no access token, `api_secret_key`, or privileged account is required — only the ability to install the app on any store (the normal, unprivileged app-install flow) or to capture one webhook delivery, after which the HMAC/body pair can be replayed indefinitely with attacker-chosen shop/topic headers.

### Recommendation
Bind the tenant-identifying and routing headers into the signed material, or otherwise cryptographically verify them: include `shop-domain`, `topic`, and `webhook-id` in `Request#to_signable_string` (matching them against the value the app expects to have installed) instead of relying solely on the raw body for the HMAC computation. At minimum, require that `Registry.process` cross-check the `shop` header against a shop for which an active, previously-established session/installation exists before invoking the handler.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture the raw body and `X-Shopify-Hmac-Sha256` value of any real webhook delivery (e.g. `orders/create` for `{}` body), which is valid because it's computed by Shopify using the app's real `api_secret_key`.
2. Replay the exact same raw body and HMAC value against the same webhook endpoint, but set:
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - `X-Shopify-Topic: shop/redact` (or any other registered topic)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which only checks the raw body against the HMAC — validation succeeds (as demonstrated by `test_process_with_new_format_headers`/`test_process_hmac_validation_fails`, which show HMAC failure is only tied to body/hmac mismatch, not to shop/topic headers): [5](#0-4) 
4. The handler is invoked with `WebhookMetadata` carrying the attacker-chosen `shop: "victim.myshopify.com"` and `topic: "shop/redact"`, causing the app to perform tenant-scoped actions against `victim.myshopify.com` on the attacker's say-so.

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

**File:** test/webhooks/registry_test.rb (L304-314)
```ruby
      def test_process_hmac_validation_fails
        headers = {
          "x-shopify-topic" => "some/topic",
          "x-shopify-hmac-sha256" => "invalid",
          "x-shopify-shop-domain" => "shop.myshopify.com",
        }

        assert_raises(ShopifyAPI::Errors::InvalidWebhookError) do
          ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers))
        end
      end
```

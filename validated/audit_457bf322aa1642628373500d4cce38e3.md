Found the identity binding break: in `lib/shopify_api/webhooks/request.rb`, the `shop` (`shop-domain`) header used to attribute an inbound webhook to a tenant is read directly from an HTTP header and is **not** included in `to_signable_string`, so it is never covered by the HMAC signature that `Utils::HmacValidator.validate` checks.

### Title
Webhook `shop-domain` header not covered by HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [2](#0-1) . `Utils::HmacValidator.validate` only verifies the HMAC over `to_signable_string` (the body) [3](#0-2) , and `Registry.process` uses that same unvalidated `request.shop` to build the `WebhookMetadata` handed to the app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop attributed to webhook == shop whose secret produced the HMAC over the body`. Because a valid HMAC only proves "this body was signed with our `api_secret_key`" and says nothing about which shop the header claims, the gem lets `Request#shop` be attacker-controlled independent of the signature. Any party capable of computing a valid HMAC for a given body over `Context.api_secret_key` (e.g., a merchant's own store legitimately receiving that webhook, or anyone who can trigger a real webhook delivery for their own tenant and then replay/relabel it) can resubmit the same signed body with a different `shopify-shop-domain` header value, and the signature will still validate since the header isn't part of the signed content. This is directly analogous to the reported bug class: a field ("shop-domain") is acted on downstream (used to key the tenant in `WebhookMetadata.new(shop: request.shop, ...)`) but is not covered by the integrity check (the HMAC), so validated bytes (body) diverge from parsed/used identity (header).

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to select which tenant's data to update/query (the intended and documented use per `Registry.process`), an attacker who can obtain one validly-HMAC-signed webhook body for their own store can relabel the `shop-domain` header to point at a victim shop, causing the app to process attacker-controlled webhook content under the victim's tenant identity — a cross-tenant data integrity/confidentiality issue if the handler trusts `shop` to scope database writes/reads.

### Likelihood Explanation
Exploitation requires the attacker to already be able to produce (or capture) one legitimately-HMAC-signed webhook payload — typically achievable by installing the app on their own store and triggering a webhook for a topic whose body they can influence (e.g., product/customer update payloads containing attacker-chosen JSON), then replaying it with a forged `shop-domain` header. No `api_secret_key`, access token, or privileged account is needed to mount the header swap itself, only receipt of one real webhook delivery for the attacker's own store.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in `to_signable_string`, or independently verify that the `shop-domain` header matches the shop associated with the session/HMAC context before dispatching to the handler, so the signed bytes and the attributed tenant identity are provably the same value.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook whose body is fully attacker-controlled content (e.g. a metafield/product update they authored), with headers `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same raw body and HMAC value to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4) , which only hashes `@raw_body` [1](#0-0)  — validation succeeds because the body/HMAC pair is unchanged.
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` [6](#0-5) , processing attacker-supplied content under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

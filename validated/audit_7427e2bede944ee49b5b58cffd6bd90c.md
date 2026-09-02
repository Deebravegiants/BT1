## Title
Webhook shop identity spoofing via HMAC that excludes the `X-Shopify-Shop-Domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an inbound webhook solely by HMAC-signing the raw request body, while the `shop` identity that the rest of the gem (and host applications) trust for tenant scoping is read from an **unsigned** header. This breaks the equality that should hold: `HMAC(raw_body, api_secret_key) valid` should imply `request.shop == the shop that actually sent this webhook`. Because `shop` is excluded from the signed bytes, any request carrying a validly-signed body (signed with the single, app-wide `api_secret_key` shared by all installed shops) can claim to originate from an arbitrary shop.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `Request#shop` is parsed straight out of the `X-Shopify-Shop-Domain` / `Shopify-Shop-Domain` header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (the raw body) against the HMAC header — it never touches `shop`: [3](#0-2) 

`Webhooks::Registry.process` then trusts `request.shop` as the tenant identifier and hands it straight to the app's handler: [4](#0-3) 

Critically, `api_secret_key` is a single, app-wide secret — the same key is used to sign webhooks for every shop that installs the app (confirmed by the test suite, which always signs with `ShopifyAPI::Context.api_secret_key` regardless of `shop`): [5](#0-4) 

This is structurally identical to the reported bug class: a field that is *acted on* (`shop`, used to scope/attribute the webhook payload to a tenant) is not covered by the HMAC that is supposed to authenticate the whole message. Any unprivileged actor who can install the target app on a shop they control receives genuinely, validly-signed webhook deliveries for that shop. Because the shop domain isn't part of the signed content, that attacker can replay/forge a POST to the app's webhook endpoint with the same valid HMAC/body but an arbitrary `X-Shopify-Shop-Domain` header, and the gem will accept it as authentic and dispatch it under that spoofed shop's identity.

### Impact Explanation
This enables cross-tenant confusion/spoofing: an attacker (an ordinary merchant who installed the app on their own store, which requires no special privilege) can make the app believe a webhook event happened for a different, victim shop. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up/create records, trigger data sync, or fulfil actions scoped to that shop), this can lead to cross-tenant data corruption or unauthorized actions attributed to a shop the attacker doesn't own — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Moderate-to-high: the attacker only needs the ability to send raw HTTP POST requests to the app's public webhook endpoint (always internet-reachable) and to have legitimately received at least one valid webhook payload for their own shop (trivial — install the app once). No access token, `client_secret`, or privileged account is required; the HMAC secret is never disclosed to the attacker, but they don't need it, because the shop identity isn't part of what's signed.

### Recommendation
Include the shop domain (and ideally webhook id/topic) inside the HMAC-signed material, or otherwise cryptographically bind `shop` to the verified signature before trusting it — e.g., verify the shop domain against records established during OAuth (a shop this app is actually installed on) rather than trusting the raw header, and/or require the HMAC to cover a canonicalized string that includes `shop-domain`, `topic`, and `webhook-id` in addition to the body.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, a shop they legitimately control.
2. Shopify delivers a real webhook to the app's endpoint with headers including a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's single `api_secret_key`, and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and resends it to the same endpoint, changing only the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com` (body untouched, so HMAC still validates because `to_signable_string` never includes the shop header):
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-value-as-original>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ...
   {"...same signed body..."}
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the HMAC: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the event never came from that shop, letting the attacker impersonate the victim tenant in the app's webhook processing logic.

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

**File:** test/webhooks/registry_test.rb (L14-28)
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
```

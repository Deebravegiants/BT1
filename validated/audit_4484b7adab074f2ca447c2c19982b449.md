### Title
Webhook Shop Domain Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` value used to attribute the webhook to a specific merchant/tenant is read from an HTTP header that is never included in the signed content. An unprivileged attacker who can capture one legitimate, HMAC-signed webhook payload (e.g. by owning/controlling a shop that installs the app) can replay that same body+HMAC pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and dispatch it to the handler under the attacker-chosen shop identity.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the supplied `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body bytes: [2](#0-1) 

But the `shop` attribute — which is used downstream as the tenant identity for the webhook — is pulled straight from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, completely outside the HMAC-covered content: [3](#0-2) 

`Registry.process` validates only the HMAC of the body and then forwards `request.shop` (the unauthenticated header value) directly into the handler's metadata as the shop of record: [4](#0-3) 

The binding that should hold is: `shop_that_signed_the_body == shop_attributed_to_the_webhook`. Because the signature never binds to the shop domain, this equality is not enforced — the HMAC only proves "this body was produced using the app's shared secret," not "this body originated from shop X." Any body+HMAC pair that was legitimately generated for one shop remains valid when replayed with a spoofed shop-domain header pointing at a different shop.

### Impact Explanation
If a webhook handler trusts `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a normal and encouraged usage pattern, since the gem hands this value to the handler as the authenticated shop), an attacker who controls one shop that has the app installed (an unprivileged, ordinary merchant — no special access needed) can capture a legitimate webhook body/HMAC pair from their own shop and re-send it against the same endpoint with a different shop-domain header, causing the app to process/attribute another tenant's data update, i.e., a cross-tenant write. This matches the "cross-tenant access" impact tier.

### Likelihood Explanation
Exploitability requires only that the attacker be a legitimate merchant of the app (or otherwise be able to observe one raw webhook body and its HMAC value, both of which are visible to the receiving endpoint's operator infrastructure/logs) and the ability to POST directly to the app's public webhook endpoint with custom headers — no secret key, access token, or privileged account is required. The gem provides no mitigation (e.g., binding shop or webhook id into the signed payload) for consumers, so any host application that follows the documented `Registry.process` flow inherits this gap.

### Recommendation
Bind the shop identity to the authenticated content before trusting it: e.g., derive/cross-check the shop against the JSON body (many Shopify webhook payloads include shop-scoped identifiers) or require callers of `Registry.process`/`WebhookHandler` to independently verify that the `shop` header matches an expected/enrolled shop for the topic+webhook id combination, and document that `request.shop` is not itself HMAC-protected so downstream consumers do not treat it as a trusted tenant identifier without additional verification (e.g., cross-referencing against a known list of shops with an active subscription for that webhook id/topic).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and subscribes to a webhook topic (e.g. `orders/create`).
2. Attacker triggers the webhook and captures the raw POST body and the `x-shopify-hmac-sha256` header value sent by Shopify to the app's endpoint.
3. Attacker resends the identical body and HMAC header to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present); `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker's order data> ...)`, causing the host application to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

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

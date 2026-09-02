## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by recomputing an HMAC over the raw request body, while the `shop`, `topic`, and `webhook_id` values used to attribute and route that payload are taken verbatim from unauthenticated HTTP headers. Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, a valid `(body, hmac)` pair from any one merchant can be replayed with a different `shop-domain` header and will still pass validation, letting an attacker misattribute a webhook payload to a different tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` treats a passing HMAC check as sufficient authorization to trust the request, then forwards the header-derived `request.shop` (and `topic`, `webhook_id`) straight to the handler as the tenant identifier, without any binding between those header values and the body that was actually signed: [3](#0-2) 

The `shop` value itself comes from an unauthenticated header, read with no cross-check against the signed bytes: [4](#0-3) 

Because the same `api_secret_key` is valid for every shop that has installed the app, a `(raw_body, hmac)` pair captured from a legitimate webhook delivered to Shop A's own installation (which the operator can trivially obtain by installing/using the app on a shop they control) remains a byte-for-byte valid signature no matter which `X-Shopify-Shop-Domain` header accompanies it. The equality the gem should be enforcing — "the shop the HMAC was computed for" == "the shop the handler is told this data belongs to" — is never checked; instead the gem only checks "bytes verified" (the body) versus "bytes parsed for tenant identity" (the header), and these are disjoint.

### Impact Explanation
This breaks the tenant boundary the webhook system is meant to preserve: an attacker who controls one shop's webhook stream can relabel a legitimate, HMAC-valid webhook body as belonging to an arbitrary other `shop-domain`, corrupting the multi-tenant guarantee that `WebhookMetadata#shop` reflects the true origin of the data being processed by the host application. This falls under the cross-tenant access category.

### Likelihood Explanation
Any developer/merchant who can install the app (a low-privilege, self-service action) can capture a valid `(body, hmac)` pair from their own webhook deliveries and replay it against the app's public webhook endpoint with an arbitrary `shop-domain` header — no access token, `client_secret`, or elevated privilege is required.

### Recommendation
Bind the authenticated identity to the signed payload rather than trusting the unauthenticated header: include the shop domain (and topic/id) inside the HMAC-signed material, or independently verify the `shop-domain` header against a known, previously-established session/shop record before passing it to `handler.handle`, rejecting the request if the header doesn't match any shop the app has legitimately installed for that specific delivery.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery — raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Send a forged HTTP POST to the app's webhook endpoint with the same body `B` and `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13`) recomputes the HMAC over `B` only, which matches `H`, so validation passes.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the handler with `shop: "victim.myshopify.com"`, even though the payload actually originated from `attacker.myshopify.com`, demonstrating the cross-tenant misattribution.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

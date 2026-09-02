## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant-spoofing on replayed/relayed webhooks - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC that is computed over the raw request body only, then hands the caller-supplied `shop-domain` header straight through to the app's handler as the tenant identifier — without that header ever being part of the signed material. This breaks the intended binding "the shop the HMAC vouches for == the shop the handler acts on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of that signable string: [2](#0-1) 

`Registry.process` verifies the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, with no cross-check that the signed body actually originated for that shop: [3](#0-2) 

`HmacValidator.validate` only recomputes the signature over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it has no notion of `shop` at all: [4](#0-3) 

Because the shop identity is carried in an *unsigned* header while only the body is signed, `Registry.process` accepts as valid any request where an attacker pairs a genuinely HMAC-signed body (for shop A, e.g., captured from their own installed app's webhook traffic, which any merchant can trivially obtain by installing the app on their own store) with a forged `shop-domain` header claiming to be shop B. The equality that should hold — "shop bound by the signature" == "shop used to route/act on the webhook" — does not hold, since the header is fully attacker-controlled and outside the MAC's protected scope.

### Impact Explanation
This is a cross-tenant identity-confusion vector: an app that uses `WebhookMetadata#shop` (as delivered by this gem) to look up per-merchant session/data before acting on the webhook body can be tricked into processing a payload under the wrong tenant's identity, since the gem itself performs no binding check between the authenticated bytes and the claimed shop. This falls under the "High: scope/binding check bypass" class described in the rubric — the shop identity used downstream is not the shop actually covered by cryptographic verification.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimately HMAC-signed webhook body (trivial for any developer/merchant who can install the target app on their own store and capture its own webhook deliveries) and then relay/replay it to the app's public webhook endpoint with a spoofed shop-domain header — no `api_secret_key` or stolen access token is required, only the ability to send an unauthenticated HTTP POST to the app's public webhook receiver, which fits the "unprivileged internet user" threat model. The library itself provides no protection against this because it never signs or validates the `shop` header.

### Recommendation
Include the shop domain (and topic) inside the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signed body (e.g., verify shop against an independently obtained, trusted source such as the registered webhook subscription/session, rather than trusting the raw header). At minimum, `Registry.process` should not treat `request.shop` as trustworthy input for anything beyond diagnostics until it has been bound to the HMAC-verified payload.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; capture a legitimately signed webhook (`x-shopify-hmac-sha256` header + raw body) delivered by Shopify for that store.
2. Replay the exact same raw body and HMAC header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `HmacValidator.validate` succeeds because it only checks the body signature:
```ruby
Utils::HmacValidator.validate(request) # => true, body/hmac pair still matches
```
4. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though the signed body never had anything to do with `victim.myshopify.com`: [5](#0-4)

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

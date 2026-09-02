### Title
Webhook shop/topic identity spoofing via HMAC that only covers the request body, not the tenant-identifying headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from unauthenticated headers. `Utils::HmacValidator` verifies the signature against that body-only string, so the HMAC never binds the shop identity to the signature. `Webhooks::Registry.process` then trusts `request.shop`/`request.topic` unconditionally and hands them to the app's webhook handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
while `shop`, `topic`, `api_version`, and `webhook_id` are pulled directly from HTTP headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate` only recomputes and compares the signature over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` performs this check and then immediately trusts the header-derived fields to build `WebhookMetadata` passed to the app's handler, with no independent validation of `shop`: [4](#0-3) 

The binding that is broken: **shop authenticated by the HMAC (i.e., "whichever body this HMAC was computed over") ≠ shop acted upon by the handler (`request.shop`, taken from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is entirely outside the signed material)**. The test suite confirms this design explicitly — the HMAC is computed only over the JSON body (`"{}"`) while the shop/topic/webhook-id headers are set independently and never included in the signed input: [5](#0-4) 

### Impact Explanation
Any unprivileged internet user can install the app on their own Shopify store and thereby legitimately receive a genuine, correctly-signed webhook delivery (raw body + valid `X-Shopify-Hmac-Sha256`) for their own shop. Because the signature covers only the body, the attacker can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `topic`/`webhook-id`) header naming a different, victim tenant. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` forwards the forged `shop` value straight into the handler via `WebhookMetadata`. Any host application that uses `request.shop`/`data.shop` to select which tenant's data or session to act on (updating local records, looking up that shop's access token for follow-up API calls, billing, inventory sync, etc.) will attribute attacker-supplied webhook content to a shop the attacker doesn't own — a cross-tenant confusion/injection vulnerability reachable without any credentials.

### Likelihood Explanation
Exploitation only requires the ability to install the target app on a shop the attacker controls (the standard, unprivileged path any merchant/developer has) and the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers — both trivially available to any internet user. No `api_secret_key`, access token, or other privileged credential is needed; the attacker only needs one legitimately-signed body/HMAC pair from their own store, which they always have.

### Recommendation
Bind the tenant/topic identity into the signed material, or independently re-verify `shop` against the caller's known/authorized shop list before acting on webhook data:
- At minimum, cross-check `request.shop` against the shop that the app's own outbound webhook registration recorded for the delivered `webhook_id`/subscription, rather than trusting the header verbatim.
- Document (and, where feasible, enforce in `Webhooks::Registry.process`) that host applications must not treat `WebhookMetadata#shop` as authenticated by the HMAC, since only the body is covered.
- Consider exposing a combined "signed context" that includes shop/topic so integrators can't accidentally rely on the unauthenticated header alone.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the exact raw body `B` and the resulting valid `X-Shopify-Hmac-Sha256` value `H` (computed by Shopify over `B` using the app's real secret).
2. Attacker sends a POST to the app's public webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and any desired `X-Shopify-Topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against `H` — this passes: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and body `B`, even though `B` and `H` were never associated with `victim-shop` by Shopify — demonstrating the header (`shop`) is unauthenticated relative to the HMAC that gated processing.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** test/webhooks/registry_test.rb (L16-28)
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
```
